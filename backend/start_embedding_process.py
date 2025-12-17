#!/usr/bin/env python3
"""
Script to start the embedding process and send data to Qdrant
"""
import os
import sys
import uuid

# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add src to path again to make imports work properly
sys.path.insert(0, src_path)

from src.embedding.services.cohere_service import CohereEmbeddingService
from src.embedding.models.content_models import ContentChunk

def process_robotics_book_content():
    """
    Process robotics book content and send embeddings to Qdrant
    """
    # Initialize the service (this will use Qdrant by default)
    service = CohereEmbeddingService()

    print("🚀 Starting embedding process...")
    print(f"📦 Using Cohere model: {service.config.model}")
    print(f"💾 Storing in Qdrant collection: robotics_embeddings")

    # Example: Create content chunks from your book
    # You'll need to replace this with your actual book content
    book_content_samples = [
        {
            "id": f"robotics-chunk-{uuid.uuid4()}",
            "text": "Forward kinematics in robotics describes the relationship between joint angles and the position and orientation of the end-effector. This mathematical model is fundamental for robot control and trajectory planning.",
            "source_file": "robotics_handbook_chapter3.pdf",
            "source_location": "page_45",
            "metadata": {"chapter": "3", "section": "3.1", "topic": "kinematics"}
        },
        {
            "id": f"robotics-chunk-{uuid.uuid4()}",
            "text": "Inverse kinematics solves the opposite problem of forward kinematics - determining the joint angles required to achieve a desired end-effector position. This is crucial for robot motion planning and control.",
            "source_file": "robotics_handbook_chapter3.pdf",
            "source_location": "page_47",
            "metadata": {"chapter": "3", "section": "3.2", "topic": "kinematics"}
        },
        {
            "id": f"robotics-chunk-{uuid.uuid4()}",
            "text": "Dexterous manipulation in robotics involves the precise control of robotic hands and fingers to handle objects with the same dexterity as human hands. This requires advanced control algorithms and tactile sensing.",
            "source_file": "robotics_handbook_chapter7.pdf",
            "source_location": "page_120",
            "metadata": {"chapter": "7", "section": "7.3", "topic": "manipulation"}
        },
        {
            "id": f"robotics-chunk-{uuid.uuid4()}",
            "text": "Gait generation for bipedal robots is a complex control problem that involves creating stable walking patterns. The challenge lies in maintaining balance while transitioning between steps, especially on uneven terrain.",
            "source_file": "robotics_handbook_chapter9.pdf",
            "source_location": "page_180",
            "metadata": {"chapter": "9", "section": "9.1", "topic": "locomotion"}
        },
        {
            "id": f"robotics-chunk-{uuid.uuid4()}",
            "text": "Balance control in humanoid robots requires real-time adjustment of the center of mass and the zero moment point. Advanced control systems use feedback from gyroscopes and accelerometers to maintain stability.",
            "source_file": "robotics_handbook_chapter9.pdf",
            "source_location": "page_185",
            "metadata": {"chapter": "9", "section": "9.2", "topic": "balance"}
        }
    ]

    # Process each chunk
    for i, content_data in enumerate(book_content_samples):
        print(f"\n📝 Processing chunk {i+1}/{len(book_content_samples)}: {content_data['id']}")

        # Create ContentChunk object
        chunk = ContentChunk(
            id=content_data["id"],
            text=content_data["text"],
            source_file=content_data["source_file"],
            source_location=content_data["source_location"],
            metadata=content_data["metadata"]
        )

        try:
            # Process the chunk - this generates embedding and stores in Qdrant
            embedding = service.process_content_chunk(chunk)
            print(f"✅ Embedding generated and stored in Qdrant")
            print(f"   • Chunk ID: {embedding.chunk_id}")
            print(f"   • Vector dimensionality: {embedding.dimensionality}")
            print(f"   • Model: {embedding.model}")
        except Exception as e:
            print(f"❌ Error processing chunk {content_data['id']}: {str(e)}")

    print(f"\n🎉 Embedding process completed!")
    print(f"📊 Total chunks processed: {len(book_content_samples)}")

def process_content_batch():
    """
    Process multiple content chunks in a batch (more efficient)
    """
    service = CohereEmbeddingService()

    # Create multiple content chunks
    chunks = []
    for i in range(3):  # Example: 3 chunks
        chunk = ContentChunk(
            id=f"robotics-batch-{i}-{uuid.uuid4()}",
            text=f"Example robotics content chunk {i+1} discussing various aspects of robotic systems, control theory, and mechanical design principles. This content is specifically crafted to demonstrate the embedding and storage capabilities of our system.",
            source_file="robotics_sample_content.txt",
            source_location=f"section_{i+1}",
            metadata={"category": "sample", "batch": "example", "topic": f"topic_{i+1}"}
        )
        chunks.append(chunk)

    print(f"📦 Processing {len(chunks)} chunks in batch mode...")

    try:
        embeddings = service.process_content_batch(chunks)
        print(f"✅ Batch processing completed! Stored {len(embeddings)} embeddings in Qdrant")
    except Exception as e:
        print(f"❌ Batch processing failed: {str(e)}")

if __name__ == "__main__":
    print("🤖 Robotics Book Embedding Pipeline")
    print("=" * 50)

    # Choose which method to run:
    # For individual processing:
    process_robotics_book_content()

    # OR for batch processing (uncomment to use):
    # process_content_batch()