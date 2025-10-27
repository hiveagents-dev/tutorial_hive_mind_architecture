"""Example execution of HiveMind architecture."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import Config
from utils.gemini_client import GeminiClient
from hivemind.architecture import HiveMindArchitecture
from hivemind.consensus import ConsensusStrategy
import json


def main():
    """Run example HiveMind execution."""

    print("=" * 80)
    print("HIVEMIND ARCHITECTURE - EXAMPLE EXECUTION")
    print("=" * 80)

    # Example business need
    business_need = """
We need to develop a mobile-first e-commerce platform for sustainable fashion brands.

Business Context:
- Target market: Millennials and Gen Z conscious consumers (ages 18-35)
- Geography: Initially launching in US, then EU expansion
- Business model: Marketplace connecting sustainable fashion brands with consumers
- Differentiation: Sustainability scoring, carbon footprint tracking, ethical certification

Key Requirements:
- Mobile apps (iOS & Android) with seamless shopping experience
- Web platform for brands to manage their stores
- Real-time inventory management
- Integrated payment processing (multiple currencies)
- Sustainability metrics and certifications display
- User reviews and ratings system
- Social features (share outfits, follow brands)

Business Goals:
- Launch MVP in 6 months
- Onboard 50 sustainable brands in first year
- Reach 100K active users in first year
- 15% conversion rate target
- Average order value of $80

Constraints:
- Budget: $500K for initial development
- Small team (5 developers, 1 designer, 1 PM)
- Must comply with GDPR and US data privacy laws
- Need to integrate with existing brand inventory systems
"""

    print("\n📝 Business Need:")
    print("-" * 80)
    print(business_need)
    print("-" * 80)

    # Initialize system
    print("\n🔧 Initializing HiveMind System...")

    try:
        config = Config()
        gemini_client = GeminiClient(
            api_key=config.get_api_key(),
            model_name=config.gemini_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )

        # Initialize with weighted voting consensus
        hivemind = HiveMindArchitecture(
            gemini_client=gemini_client,
            consensus_strategy=ConsensusStrategy.WEIGHTED_VOTING
        )

        print("✅ System initialized successfully!")
        print(f"   Workers: {len(hivemind.worker_agents)}")
        print(f"   Consensus: {hivemind.consensus_strategy.value}")

        # Execute
        print("\n🚀 Starting HiveMind analysis...\n")

        result = hivemind.execute(business_need, verbose=True)

        # Display final requirements (abbreviated)
        print("\n" + "=" * 80)
        print("FINAL TECHNICAL REQUIREMENTS (Summary)")
        print("=" * 80)

        try:
            requirements = json.loads(result.supervisor_response.content)

            print("\n📄 Document Metadata:")
            print(f"   Title: {requirements['document_metadata']['title']}")
            print(f"   Version: {requirements['document_metadata']['version']}")
            print(f"   Status: {requirements['document_metadata']['status']}")

            print("\n🎯 Executive Summary:")
            exec_sum = requirements['executive_summary']
            print(f"   Overview: {exec_sum['overview'][:200]}...")
            print(f"   Timeline: {exec_sum['timeline']}")

            print("\n🔧 Technology Stack:")
            tech = requirements['technical_specifications']['technology_stack']
            print(f"   Frontend: {', '.join([t['technology'] for t in tech.get('frontend', [])])}")
            print(f"   Backend: {', '.join([t['technology'] for t in tech.get('backend', [])])}")

            print("\n📊 Key Risks:")
            for risk in requirements['risks_and_mitigation'][:3]:
                print(f"   • {risk['description'][:100]}...")

            # Save to file
            output_file = Path(__file__).parent / "example_requirements.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(requirements, f, indent=2)

            print(f"\n💾 Full requirements saved to: {output_file}")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Could not parse requirements JSON: {e}")
            print("\nRaw response:")
            print(result.supervisor_response.content[:500])

        # Communication statistics
        print("\n📞 Communication Statistics:")
        stats = hivemind.get_communication_statistics()
        print(f"   Total messages: {stats['total_messages']}")
        print(f"   Agents involved: {stats['agent_count']}")
        print(f"   Duration: {result.execution_time:.2f}s")

        print("\n" + "=" * 80)
        print("✅ EXAMPLE EXECUTION COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
