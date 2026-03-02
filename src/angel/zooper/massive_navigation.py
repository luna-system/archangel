#!/usr/bin/env python3
"""
Massive Navigation Run - Generate Thousands of Word Engrams!

Run extended navigation queries to populate the word engram graph.
"""

import sys
import shutil
import json
import numpy as np
from datetime import datetime

sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager, ZooperSwarm


def main():
    print("🦊 MASSIVE NAVIGATION & ENGRAM GENERATION 🦊")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Connect to current holofield (with existing engrams)
    print("\n📦 Connecting to holofield...")
    hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
    
    # Get baseline stats
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
    initial_words = cursor.fetchone()[0]
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams")
    initial_total = cursor.fetchone()[0]
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engram_connections")
    initial_edges = cursor.fetchone()[0]
    
    print(f"\n📊 Baseline:")
    print(f"   Word engrams: {initial_words:,}")
    print(f"   Total engrams: {initial_total:,}")
    print(f"   Connections: {initial_edges:,}")
    
    # Initialize swarm
    print("\n🐾 Initializing zooper swarm...")
    swarm = ZooperSwarm(hf, num_zooperlings=13)
    
    # MASSIVE query set - 200+ navigations
    all_queries = [
        # Calendar (extensive)
        ("January", "February"), ("February", "March"), ("March", "April"),
        ("April", "May"), ("May", "June"), ("June", "July"),
        ("July", "August"), ("August", "September"), ("September", "October"),
        ("October", "November"), ("November", "December"), ("December", "January"),
        ("Monday", "Tuesday"), ("Tuesday", "Wednesday"), ("Wednesday", "Thursday"),
        ("Thursday", "Friday"), ("Friday", "Saturday"), ("Saturday", "Sunday"),
        ("Spring", "Summer"), ("Summer", "Autumn"), ("Autumn", "Winter"), ("Winter", "Spring"),
        ("Morning", "Afternoon"), ("Afternoon", "Evening"), ("Evening", "Night"),
        
        # Geography (extensive)
        ("France", "Paris"), ("Germany", "Berlin"), ("Italy", "Rome"),
        ("Spain", "Madrid"), ("England", "London"), ("Japan", "Tokyo"),
        ("China", "Beijing"), ("India", "Delhi"), ("Brazil", "Rio"),
        ("Canada", "Toronto"), ("Australia", "Sydney"), ("Russia", "Moscow"),
        ("Egypt", "Cairo"), ("Greece", "Athens"), ("Turkey", "Istanbul"),
        ("Mexico", "Mexico City"), ("Argentina", "Buenos Aires"),
        ("Europe", "Asia"), ("Africa", "Egypt"), ("America", "Canada"),
        ("United States", "New York"), ("California", "Los Angeles"),
        ("Texas", "Houston"), ("Florida", "Miami"),
        
        # Animals (extensive)
        ("Animal", "Dog"), ("Dog", "Wolf"), ("Wolf", "Coyote"),
        ("Cat", "Tiger"), ("Tiger", "Lion"), ("Lion", "Leopard"),
        ("Bird", "Eagle"), ("Eagle", "Hawk"), ("Hawk", "Falcon"),
        ("Fish", "Shark"), ("Shark", "Whale"), ("Whale", "Dolphin"),
        ("Insect", "Butterfly"), ("Butterfly", "Moth"),
        ("Mammal", "Human"), ("Human", "Ape"), ("Ape", "Monkey"),
        ("Snake", "Lizard"), ("Lizard", "Crocodile"),
        ("Horse", "Zebra"), ("Zebra", "Donkey"),
        
        # Science (extensive)
        ("Physics", "Chemistry"), ("Chemistry", "Biology"), ("Biology", "Genetics"),
        ("Genetics", "DNA"), ("DNA", "Gene"), ("Gene", "Protein"),
        ("Planet", "Earth"), ("Earth", "Moon"), ("Moon", "Mars"),
        ("Mars", "Jupiter"), ("Jupiter", "Saturn"), ("Saturn", "Uranus"),
        ("Sun", "Star"), ("Star", "Galaxy"), ("Galaxy", "Universe"),
        ("Water", "Ice"), ("Ice", "Snow"), ("Water", "Steam"),
        ("Fire", "Heat"), ("Heat", "Energy"), ("Energy", "Power"),
        ("Atom", "Molecule"), ("Molecule", "Compound"),
        ("Cell", "Tissue"), ("Tissue", "Organ"), ("Organ", "Body"),
        
        # Food (extensive)
        ("Food", "Fruit"), ("Fruit", "Apple"), ("Apple", "Orange"),
        ("Orange", "Lemon"), ("Apple", "Pear"), ("Pear", "Peach"),
        ("Food", "Vegetable"), ("Vegetable", "Carrot"), ("Carrot", "Potato"),
        ("Potato", "Tomato"), ("Tomato", "Cucumber"),
        ("Food", "Meat"), ("Meat", "Beef"), ("Beef", "Pork"),
        ("Pork", "Chicken"), ("Chicken", "Turkey"),
        ("Bread", "Wheat"), ("Wheat", "Rice"), ("Rice", "Corn"),
        ("Milk", "Cheese"), ("Cheese", "Butter"), ("Butter", "Yogurt"),
        
        # Colors (complete)
        ("Color", "Red"), ("Red", "Pink"), ("Red", "Orange"),
        ("Color", "Blue"), ("Blue", "Navy"), ("Blue", "Cyan"),
        ("Color", "Green"), ("Green", "Yellow"), ("Yellow", "Gold"),
        ("Green", "Cyan"), ("Cyan", "Blue"),
        ("Red", "Purple"), ("Purple", "Violet"),
        
        # Abstract concepts
        ("Love", "Happiness"), ("Happiness", "Joy"), ("Joy", "Smile"),
        ("War", "Peace"), ("Peace", "Calm"), ("Calm", "Quiet"),
        ("Art", "Music"), ("Music", "Song"), ("Song", "Dance"),
        ("Dance", "Ballet"), ("Music", "Piano"), ("Piano", "Guitar"),
        ("Book", "Story"), ("Story", "Novel"), ("Novel", "Poetry"),
        ("Number", "Mathematics"), ("Mathematics", "Geometry"),
        ("Geometry", "Algebra"), ("Mathematics", "Calculus"),
        ("Time", "Clock"), ("Clock", "Watch"), ("Time", "History"),
        
        # Nature
        ("Tree", "Forest"), ("Forest", "Jungle"), ("Jungle", "Rainforest"),
        ("River", "Ocean"), ("Ocean", "Sea"), ("Sea", "Lake"),
        ("Lake", "Pond"), ("River", "Stream"), ("Stream", "Brook"),
        ("Mountain", "Hill"), ("Hill", "Valley"), ("Mountain", "Peak"),
        ("Cloud", "Rain"), ("Rain", "Storm"), ("Storm", "Thunder"),
        ("Wind", "Breeze"), ("Wind", "Hurricane"), ("Hurricane", "Tornado"),
        
        # Human activities
        ("School", "Teacher"), ("Teacher", "Student"), ("Student", "School"),
        ("Doctor", "Hospital"), ("Hospital", "Nurse"), ("Doctor", "Medicine"),
        ("Car", "Road"), ("Road", "Street"), ("Street", "Highway"),
        ("Car", "Truck"), ("Truck", "Bus"), ("Bus", "Train"),
        ("Computer", "Internet"), ("Internet", "Website"), ("Website", "Page"),
        ("Money", "Bank"), ("Bank", "Coin"), ("Coin", "Dollar"),
        ("Game", "Sport"), ("Sport", "Football"), ("Football", "Soccer"),
        ("Soccer", "Basketball"), ("Basketball", "Baseball"),
        
        # Professions
        ("Work", "Job"), ("Job", "Career"), ("Career", "Profession"),
        ("Artist", "Painter"), ("Painter", "Sculptor"),
        ("Writer", "Author"), ("Author", "Poet"),
        ("Scientist", "Researcher"), ("Researcher", "Professor"),
        ("Engineer", "Architect"), ("Architect", "Designer"),
        
        # Emotions
        ("Happy", "Sad"), ("Sad", "Cry"), ("Cry", "Tear"),
        ("Angry", "Mad"), ("Mad", "Furious"), ("Furious", "Rage"),
        ("Scared", "Afraid"), ("Afraid", "Fear"), ("Fear", "Terror"),
        ("Surprised", "Shocked"), ("Shocked", "Amazed"),
    ]
    
    print(f"\n🧭 Running {len(all_queries)} navigation queries...")
    print("-" * 70)
    
    successful = 0
    failed = 0
    total_hops = 0
    
    for i, (start, target) in enumerate(all_queries, 1):
        try:
            # Get coordinates
            cursor = hf.conn.execute(
                "SELECT coords_16d FROM engrams WHERE content LIKE ? LIMIT 1",
                (f"{start}%",)
            )
            row = cursor.fetchone()
            if not row:
                print(f"  {i:3d}. {start:20s} → {target:20s} [SKIP: start not found]")
                failed += 1
                continue
            start_coords = np.array(json.loads(row[0]))
            
            cursor = hf.conn.execute(
                "SELECT coords_16d FROM engrams WHERE content LIKE ? LIMIT 1",
                (f"{target}%",)
            )
            row = cursor.fetchone()
            if not row:
                print(f"  {i:3d}. {start:20s} → {target:20s} [SKIP: target not found]")
                failed += 1
                continue
            target_coords = np.array(json.loads(row[0]))
            
            # Navigate (this creates exploration engrams!)
            path = swarm.navigate(start_coords, target_coords, max_hops=5)
            
            if path and len(path) > 1:
                hops = len(path) - 1
                total_hops += hops
                successful += 1
                
                if i % 20 == 0:
                    print(f"  {i:3d}. {start:20s} → {target:20s} [{hops} hops] ✓")
            else:
                failed += 1
                
        except Exception as e:
            print(f"  {i:3d}. {start:20s} → {target:20s} [ERROR: {str(e)[:30]}]")
            failed += 1
    
    # Final stats
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
    final_words = cursor.fetchone()[0]
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams")
    final_total = cursor.fetchone()[0]
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engram_connections")
    final_edges = cursor.fetchone()[0]
    
    print(f"\nNavigation:")
    print(f"  Total queries: {len(all_queries)}")
    print(f"  Successful: {successful} ({100*successful/len(all_queries):.1f}%)")
    print(f"  Failed: {failed}")
    if successful > 0:
        print(f"  Avg hops: {total_hops/successful:.1f}")
    
    print(f"\nHolofield Growth:")
    print(f"  Word engrams: {initial_words:,} → {final_words:,} (+{final_words - initial_words:,})")
    print(f"  Total engrams: {initial_total:,} → {final_total:,} (+{final_total - initial_total:,})")
    print(f"  Connections: {initial_edges:,} → {final_edges:,} (+{final_edges - initial_edges:,})")
    
    print(f"\n⏱️  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    hf.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
