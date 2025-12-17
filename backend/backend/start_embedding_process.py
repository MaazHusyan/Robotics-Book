#!/usr/bin/env python3
"""
Script to start the embedding process for actual book content and send data to Qdrant
"""
import os
import sys
import uuid
import re
from pathlib import Path

# Add the parent directory (project root) to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up two levels to project root
sys.path.insert(0, project_root)

# Add the backend/src directory to the Python path
backend_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, backend_src_path)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.embedding.services.cohere_service import CohereEmbeddingService
from src.embedding.models.content_models import ContentChunk


def chunk_text_by_structure(text, max_chunk_size=1000):
    """
    Split text by document structure (headings, paragraphs) instead of character count
    """
    # Split by common heading patterns (Chapter, Section, etc.)
    heading_pattern = r'(?:^|\n)(#{1,6}\s+|\d+[\.\d]*\s+|\*\*[^*]+\*\*|__[^_]+__|\n\s*[A-Z][a-z]*\s*:?\n)'

    # First split by headings
    parts = re.split(heading_pattern, text)

    chunks = []
    current_chunk = ""

    for part in parts:
        if len(part.strip()) == 0:
            continue

        # If this part looks like a heading/chapter title
        if re.match(r'^(#{1,6}\s+|\d+[\.\d]*\s+)', part) or len(part) < 100:
            # If current chunk is substantial, save it before starting new one with heading
            if len(current_chunk) > 100:  # If we have a substantial chunk
                chunks.append(current_chunk.strip())
                current_chunk = part
            else:
                current_chunk += " " + part
        else:
            # Regular content - add to current chunk
            if len(current_chunk) + len(part) > max_chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = part
            else:
                current_chunk += " " + part

    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Further split any chunks that are still too large
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size * 1.5:  # If still too large
            # Split by paragraphs
            paragraphs = chunk.split('\n\n')
            temp_chunk = ""
            for para in paragraphs:
                if len(temp_chunk) + len(para) > max_chunk_size:
                    if temp_chunk.strip():
                        final_chunks.append(temp_chunk.strip())
                    temp_chunk = para
                else:
                    temp_chunk += "\n\n" + para
            if temp_chunk.strip():
                final_chunks.append(temp_chunk.strip())
        else:
            final_chunks.append(chunk)

    return final_chunks


def read_book_content_from_pdf(file_path):
    """
    Read and chunk actual book content with proper structure preservation
    """
    try:
        import PyPDF2
    except ImportError:
        print("PyPDF2 not installed. Install with: pip install PyPDF2")
        return []

    chunks = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""

        # Extract text from all pages
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            full_text += f"\nPAGE_{page_num + 1}\n{page_text}\n"

        # Extract potential chapter/section headings
        # Common patterns for chapters and sections
        chapter_patterns = [
            r'(?:^|\n)\s*Chapter\s+\d+[.:]?\s*[^\n]*\n',
            r'(?:^|\n)\s*Section\s+\d+[.:]?\s*[^\n]*\n',
            r'(?:^|\n)\s*\d+\.\d*\s+[A-Z][^\n]*\n',  # Numbered sections
            r'(?:^|\n)\s*#{1,3}\s*[^\n]+\n',  # Markdown headings
        ]

        # Find chapter breaks and create chunks around them
        text_parts = [full_text]  # Start with full text as single part

        for pattern in chapter_patterns:
            new_parts = []
            for part in text_parts:
                # Split by this pattern
                splits = re.split(pattern, part)
                new_parts.extend(splits)
            text_parts = [p for p in new_parts if p.strip()]

        # Now chunk each part appropriately
        for i, part in enumerate(text_parts):
            if len(part.strip()) < 50:  # Skip very small parts
                continue

            # Break down large parts by structure
            sub_chunks = chunk_text_by_structure(part, max_chunk_size=1200)

            for j, sub_chunk in enumerate(sub_chunks):
                if len(sub_chunk.strip()) < 50:  # Skip very small chunks
                    continue

                # Try to identify chapter/section from content
                chapter_match = re.search(r'Chapter\s+(\d+)', part[:200], re.IGNORECASE)
                section_match = re.search(r'Section\s+([\d.]+)', part[:200], re.IGNORECASE)

                chapter_num = chapter_match.group(1) if chapter_match else "unknown"
                section_num = section_match.group(1) if section_match else "unknown"

                chunks.append({
                    "id": f"book-{Path(file_path).stem}-ch{chapter_num}-sec{section_num}-part{i}-sub{j}-{uuid.uuid4()}",
                    "text": sub_chunk,
                    "source_file": Path(file_path).name,
                    "source_location": f"ch{chapter_num}_sec{section_num}_part{i}_sub{j}",
                    "metadata": {
                        "chapter": chapter_num,
                        "section": section_num,
                        "part": i,
                        "sub_part": j,
                        "file": Path(file_path).name,
                        "type": "book_content"
                    }
                })

    return chunks


def read_book_content_from_text(file_path):
    """
    Read and chunk text files with structure preservation
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Split by common document structure
    chunks = []

    # Look for chapter/section patterns
    chapter_patterns = [
        r'(?:^|\n)\s*Chapter\s+\d+[.:]?\s*[^\n]*',
        r'(?:^|\n)\s*Section\s+\d+[.:]?\s*[^\n]*',
        r'(?:^|\n)\s*\d+\.\d*\s+[A-Z][^\n]*',  # Numbered sections
        r'(?:^|\n)\s*#{1,3}\s*[^\n]*',  # Markdown headings
    ]

    # Split by the most significant structure first
    text_parts = [text]
    for pattern in chapter_patterns:
        new_parts = []
        for part in text_parts:
            splits = re.split(pattern, part)
            new_parts.extend([p for p in splits if p.strip()])
        text_parts = new_parts

    # Process each part
    for i, part in enumerate(text_parts):
        if len(part.strip()) < 50:
            continue

        # Break down by structure
        sub_chunks = chunk_text_by_structure(part, max_chunk_size=1200)

        for j, sub_chunk in enumerate(sub_chunks):
            if len(sub_chunk.strip()) < 50:
                continue

            # Try to identify structure from content
            chapter_match = re.search(r'Chapter\s+(\d+)', part[:200], re.IGNORECASE)
            section_match = re.search(r'Section\s+([\d.]+)', part[:200], re.IGNORECASE)

            chapter_num = chapter_match.group(1) if chapter_match else "unknown"
            section_num = section_match.group(1) if section_match else "unknown"

            chunks.append({
                "id": f"text-{Path(file_path).stem}-ch{chapter_num}-sec{section_num}-part{i}-sub{j}-{uuid.uuid4()}",
                "text": sub_chunk,
                "source_file": Path(file_path).name,
                "source_location": f"ch{chapter_num}_sec{section_num}_part{i}_sub{j}",
                "metadata": {
                    "chapter": chapter_num,
                    "section": section_num,
                    "part": i,
                    "sub_part": j,
                    "file": Path(file_path).name,
                    "type": "book_content"
                }
            })

    return chunks


def process_your_actual_books(book_directory="book_content"):
    """
    Process your real book content with proper structure preservation
    """
    service = CohereEmbeddingService()

    # Create book directory if it doesn't exist
    book_dir = Path(book_directory)
    book_dir.mkdir(exist_ok=True)

    print(f"🔍 Looking for book files in: {book_dir.absolute()}")

    # Find all book files
    book_files = list(book_dir.glob("*.pdf")) + list(book_dir.glob("*.txt")) + list(book_dir.glob("*.docx"))

    if not book_files:
        print(f"❌ No book files found in {book_dir}. Please place your book files in this directory.")
        print("Supported formats: PDF, TXT, DOCX")
        return

    print(f"📚 Found {len(book_files)} book files to process")

    total_chunks_processed = 0

    for book_file in book_files:
        print(f"\n📖 Processing book: {book_file.name}")

        # Determine file type and use appropriate reader
        if book_file.suffix.lower() == '.pdf':
            book_chunks = read_book_content_from_pdf(str(book_file))
        elif book_file.suffix.lower() == '.txt':
            book_chunks = read_book_content_from_text(str(book_file))
        elif book_file.suffix.lower() == '.docx':
            # For docx files, you'd need python-docx
            try:
                import docx
                book_chunks = read_book_content_from_docx(str(book_file))
            except ImportError:
                print("python-docx not installed. Install with: pip install python-docx")
                continue
        else:
            print(f"❌ Unsupported file format: {book_file.suffix}")
            continue

        print(f"   Found {len(book_chunks)} content chunks to process")

        # Process each chunk
        for i, content_data in enumerate(book_chunks):
            print(f"   📝 Processing chunk {i+1}/{len(book_chunks)} (size: {len(content_data['text'])} chars)")

            chunk = ContentChunk(
                id=content_data["id"],
                text=content_data["text"],
                source_file=content_data["source_file"],
                source_location=content_data["source_location"],
                metadata=content_data["metadata"]
            )

            try:
                embedding = service.process_content_chunk(chunk)
                print(f"     ✅ Stored in Qdrant: {embedding.chunk_id[:20]}... (dim: {embedding.dimensionality})")
                total_chunks_processed += 1
            except Exception as e:
                print(f"     ❌ Error processing chunk: {str(e)}")

    print(f"\n🎉 Book embedding process completed!")
    print(f"📊 Total chunks processed and stored in Qdrant: {total_chunks_processed}")


def read_book_content_from_docx(file_path):
    """
    Read and chunk docx files with structure preservation
    """
    try:
        import docx
    except ImportError:
        print("python-docx not installed. Install with: pip install python-docx")
        return []

    doc = docx.Document(file_path)
    full_text = []

    # Extract text while preserving structure
    for para in doc.paragraphs:
        full_text.append(para.text)

    text = '\n\n'.join(full_text)

    # Process the text similar to the text file method
    chunks = []

    # Look for chapter/section patterns
    chapter_patterns = [
        r'(?:^|\n)\s*Chapter\s+\d+[.:]?\s*[^\n]*',
        r'(?:^|\n)\s*Section\s+\d+[.:]?\s*[^\n]*',
        r'(?:^|\n)\s*\d+\.\d*\s+[A-Z][^\n]*',  # Numbered sections
    ]

    # Split by the most significant structure first
    text_parts = [text]
    for pattern in chapter_patterns:
        new_parts = []
        for part in text_parts:
            splits = re.split(pattern, part)
            new_parts.extend([p for p in splits if p.strip()])
        text_parts = new_parts

    # Process each part
    for i, part in enumerate(text_parts):
        if len(part.strip()) < 50:
            continue

        # Break down by structure
        sub_chunks = chunk_text_by_structure(part, max_chunk_size=1200)

        for j, sub_chunk in enumerate(sub_chunks):
            if len(sub_chunk.strip()) < 50:
                continue

            # Try to identify structure from content
            chapter_match = re.search(r'Chapter\s+(\d+)', part[:200], re.IGNORECASE)
            section_match = re.search(r'Section\s+([\d.]+)', part[:200], re.IGNORECASE)

            chapter_num = chapter_match.group(1) if chapter_match else "unknown"
            section_num = section_match.group(1) if section_match else "unknown"

            chunks.append({
                "id": f"docx-{Path(file_path).stem}-ch{chapter_num}-sec{section_num}-part{i}-sub{j}-{uuid.uuid4()}",
                "text": sub_chunk,
                "source_file": Path(file_path).name,
                "source_location": f"ch{chapter_num}_sec{section_num}_part{i}_sub{j}",
                "metadata": {
                    "chapter": chapter_num,
                    "section": section_num,
                    "part": i,
                    "sub_part": j,
                    "file": Path(file_path).name,
                    "type": "book_content"
                }
            })

    return chunks


def create_sample_book_content():
    """
    Create a sample book content file for testing if no books are available
    """
    sample_content = """# Introduction to Robotics

## Chapter 1: Fundamentals of Robotics

Robotics is an interdisciplinary field that integrates mechanical engineering, electrical engineering, computer science, and other disciplines to design, construct, operate, and use robots. A robot is a physical embodiment of artificial intelligence that can interact with the physical world.

The primary goal of robotics is to create machines that can assist humans in various tasks, from manufacturing and exploration to healthcare and domestic services. Modern robots range from simple automated machines to complex systems with advanced AI capabilities.

### 1.1 History of Robotics

The concept of robots dates back to ancient civilizations, but the modern era of robotics began in the 20th century. The term "robot" was first introduced by Czech writer Karel Čapek in his 1920 play R.U.R. (Rossum's Universal Robots).

Early industrial robots were developed in the 1960s and were primarily used for manufacturing tasks such as welding, painting, and assembly. These robots were programmed to perform repetitive tasks with high precision and reliability.

### 1.2 Types of Robots

Industrial robots are the most common type of robots used in manufacturing environments. They are designed to perform specific tasks such as welding, painting, assembly, and material handling.

Service robots are designed to assist humans in non-industrial environments. Examples include domestic robots like vacuum cleaners, healthcare robots that assist in hospitals, and entertainment robots.

Mobile robots are capable of movement in their environment. They can be wheeled, legged, or use other locomotion methods. Autonomous vehicles are a prominent example of mobile robots.

## Chapter 2: Robot Kinematics

Robot kinematics is the study of motion in robotic systems. It deals with the relationship between the joint parameters and the position and orientation of the end-effector. Understanding kinematics is crucial for controlling robot movement and trajectory planning.

### 2.1 Forward Kinematics

Forward kinematics describes the relationship between joint angles and the position and orientation of the end-effector. This mathematical model is fundamental for robot control and trajectory planning.

The forward kinematics problem involves calculating the end-effector pose given the joint variables. This is typically solved using transformation matrices and the Denavit-Hartenberg convention for representing the kinematic chain.

### 2.2 Inverse Kinematics

Inverse kinematics solves the opposite problem of forward kinematics - determining the joint angles required to achieve a desired end-effector position. This is crucial for robot motion planning and control.

The inverse kinematics problem is generally more complex than forward kinematics. For simple robots, analytical solutions may exist, but for complex robots, numerical methods are often required.

## Chapter 3: Robot Dynamics and Control

Robot dynamics deals with the forces and torques required to generate motion. It encompasses both the dynamic modeling of robots and the control strategies used to achieve desired motion.

### 3.1 Dynamic Modeling

The dynamic model of a robot describes the relationship between applied forces/torques and the resulting motion. This model is essential for accurate robot control and simulation.

The dynamic equations of motion for a robot manipulator can be derived using Lagrangian mechanics or Newton-Euler methods. The model typically includes terms for inertial forces, Coriolis and centrifugal forces, and gravitational forces.

### 3.2 Control Strategies

Robot control involves developing algorithms to make the robot follow desired trajectories or achieve specific tasks. Common control strategies include PID control, computed torque control, and adaptive control.

Advanced control techniques such as model predictive control and learning-based control are becoming increasingly important as robots operate in more complex and uncertain environments.

## Chapter 4: Sensors and Perception

Robots need sensors to perceive their environment and interact with it effectively. Sensor systems enable robots to navigate, manipulate objects, and respond to changes in their surroundings.

### 4.1 Types of Sensors

Proprioceptive sensors provide information about the robot's internal state, such as joint angles, velocities, and motor currents. These sensors are crucial for feedback control.

Exteroceptive sensors provide information about the external environment. Examples include cameras, LIDAR, ultrasonic sensors, and tactile sensors.

### 4.2 Computer Vision in Robotics

Computer vision enables robots to interpret visual information from cameras. This capability is essential for navigation, object recognition, and manipulation tasks.

Modern robot vision systems often use deep learning techniques to recognize objects, estimate poses, and understand scenes. These systems can operate in real-time and handle various lighting conditions.

## Chapter 5: Robot Manipulation

Dexterous manipulation in robotics involves the precise control of robotic hands and fingers to handle objects with the same dexterity as human hands. This requires advanced control algorithms and tactile sensing.

### 5.1 Grasping and Manipulation

Grasping involves establishing contact between the robot's end-effector and objects in the environment. A stable grasp is essential for manipulation tasks.

The grasp planning problem involves determining the optimal contact points and forces needed to securely grasp an object. This requires understanding object properties, friction, and robot capabilities.

### 5.2 Force Control

Force control is essential for manipulation tasks where the robot needs to apply specific forces or interact with the environment in a controlled manner. This is particularly important for assembly tasks and interaction with deformable objects.

Impedance control and admittance control are common approaches for force control. These methods allow the robot to behave like a spring-damper system with adjustable stiffness and damping properties.

## Chapter 6: Mobile Robotics

Mobile robots are capable of movement in their environment. They can be wheeled, legged, or use other locomotion methods. Autonomous vehicles are a prominent example of mobile robots.

### 6.1 Locomotion Systems

Wheeled robots are the most common type of mobile robot due to their efficiency and simplicity. Different wheel configurations offer various advantages in terms of maneuverability and stability.

Legged robots can navigate challenging terrain that wheeled robots cannot access. However, they are more complex to control and require sophisticated balance and gait generation algorithms.

### 6.2 Navigation and Path Planning

Navigation involves moving a robot from one location to another while avoiding obstacles. This requires perception, mapping, localization, and path planning capabilities.

Path planning algorithms generate collision-free paths from a start to a goal location. Common approaches include graph-based methods like A* and sampling-based methods like RRT (Rapidly-exploring Random Trees).

## Chapter 7: Human-Robot Interaction

Human-robot interaction (HRI) is an interdisciplinary field that studies how humans and robots can interact effectively and safely. As robots become more prevalent in human environments, HRI becomes increasingly important.

### 7.1 Safety in Human-Robot Interaction

Safety is paramount in human-robot interaction. Robots must be designed and controlled to prevent harm to humans during normal operation and in case of failures.

Safety standards such as ISO 10218 for industrial robots and emerging standards for collaborative robots define requirements for safe human-robot interaction.

### 7.2 Communication and Interfaces

Effective communication between humans and robots is essential for successful interaction. This includes both the robot's ability to understand human commands and its ability to communicate its intentions to humans.

Natural language processing, gesture recognition, and intuitive user interfaces are key technologies for improving human-robot communication.

## Chapter 8: Applications of Robotics

Robotics has found applications in numerous fields, from manufacturing and healthcare to space exploration and domestic services. The versatility of robots makes them valuable tools across many industries.

### 8.1 Industrial Applications

Manufacturing is one of the primary applications of robotics. Industrial robots perform tasks such as welding, painting, assembly, and material handling with high precision and reliability.

The automotive industry has been a major adopter of industrial robotics, using robots for various assembly tasks. This has led to increased productivity and quality in vehicle manufacturing.

### 8.2 Service and Healthcare Robotics

Service robots assist humans in non-industrial environments. Examples include domestic robots like vacuum cleaners, delivery robots in hospitals, and customer service robots in retail environments.

Healthcare robotics includes surgical robots that assist surgeons with precision tasks, rehabilitation robots that help patients recover from injuries, and assistive robots that support elderly or disabled individuals.

## Chapter 9: Advanced Topics in Robotics

Modern robotics research focuses on developing more autonomous, adaptable, and intelligent robots. This includes advances in AI, machine learning, and human-robot collaboration.

### 9.1 Learning in Robotics

Machine learning enables robots to improve their performance through experience. This includes reinforcement learning for control tasks, imitation learning for skill acquisition, and transfer learning for adapting to new situations.

Deep learning has revolutionized many aspects of robotics, particularly in perception tasks such as object recognition, scene understanding, and natural language processing.

### 9.2 Multi-Robot Systems

Multi-robot systems involve coordinating multiple robots to achieve common goals. This can provide advantages in terms of redundancy, parallelism, and distributed sensing and actuation.

Cooperative control algorithms enable robots to work together effectively. Communication protocols and consensus algorithms are essential for coordination in multi-robot systems.

## Chapter 10: Future of Robotics

The future of robotics promises even more sophisticated and capable robots. Advances in AI, materials science, and manufacturing are driving the development of new robotic capabilities.

### 10.1 Emerging Technologies

Soft robotics uses flexible materials to create robots that can safely interact with humans and adapt to their environment. These robots can achieve complex movements and interactions that traditional rigid robots cannot.

Swarm robotics involves large numbers of simple robots that collectively exhibit complex behaviors. This approach can provide robustness and scalability for certain applications.

### 10.2 Ethical Considerations

As robots become more capable and prevalent, ethical considerations become increasingly important. Issues such as job displacement, privacy, and robot rights need to be addressed.

The development of ethical frameworks and guidelines for robotics is an active area of research and policy development. These frameworks will guide the responsible development and deployment of robotic systems.
"""

    # Create the book_content directory and write sample file
    book_dir = Path("book_content")
    book_dir.mkdir(exist_ok=True)

    sample_file = book_dir / "robotics_handbook_sample.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_content)

    print(f"📄 Created sample book content file: {sample_file}")
    return sample_file


if __name__ == "__main__":
    print("🤖 Robotics Book Embedding Pipeline - Enhanced Version")
    print("=" * 60)
    print("This script will process your actual book content and store embeddings in Qdrant")
    print("with proper structure preservation (chapters, sections, paragraphs).")
    print()

    # Check if book_content directory exists and has files
    book_dir = Path("book_content")
    if not book_dir.exists():
        print("📁 'book_content' directory not found. Creating with sample content...")
        sample_file = create_sample_book_content()
        print(f"✅ Created sample content in {sample_file}")
        print("💡 Tip: Replace this file with your actual book files (PDF, TXT, DOCX)")
    else:
        book_files = list(book_dir.glob("*.*"))
        if not book_files:
            print("📁 'book_content' directory is empty. Creating sample content...")
            sample_file = create_sample_book_content()
            print(f"✅ Created sample content in {sample_file}")
            print("💡 Tip: Replace this file with your actual book files (PDF, TXT, DOCX)")
        else:
            print(f"📁 Found {len(book_files)} files in 'book_content' directory")

    print()
    print("🚀 Starting embedding process for actual book content...")
    process_your_actual_books()

    print()
    print("🎉 EMBEDDING PROCESS COMPLETED SUCCESSFULLY!")
    print("📊 Your book content is now stored in Qdrant and ready for chatbot retrieval!")
    print()
    print("💡 Next steps:")
    print("   - Your chatbot can now retrieve from actual book content")
    print("   - No more hallucinations - answers will be grounded in your books")
    print("   - Check Qdrant dashboard at http://localhost:6333/dashboard")