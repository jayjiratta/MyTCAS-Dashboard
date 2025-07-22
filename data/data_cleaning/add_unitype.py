import json
import urllib.parse

json_path = 'data/data_cleaning/output_with_tuition.json'

# Read the current JSON file
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get unique universities
universities = set()
for item in data:
    if 'university' in item and item['university']:
        universities.add(item['university'])

universities = sorted(list(universities))

print("🔥 Interactive University Classification Tool")
print("=" * 50)
print("📋 Instructions:")
print("- Click the link to open in Firefox")
print("- Type 't' for Public university")
print("- Type 'f' for Private university")
print("- Type 'q' to quit the program")
print("=" * 50)

# Process each university
for i, university in enumerate(universities):
    print(f"\n🏫 [{i+1}/{len(universities)}] {university}")
    
    # Create search query
    search_query = f"{university} เป็นมหาวิทยาลัยรัฐหรือเอกชน"
    encoded_query = urllib.parse.quote(search_query)
    firefox_url = f"https://www.google.com/search?q={encoded_query}"
    
    print(f"🔗 Firefox Link: {firefox_url}")
    
    # Get user input
    while True:
        choice = input("\n👉 Enter classification (t=Public, f=Private, q=Quit): ").lower().strip()
        
        if choice == 'q':
            print("👋 Exiting program...")
            exit()
        elif choice == 't':
            is_public = True
            print("✅ Classified as PUBLIC university")
            break
        elif choice == 'f':
            is_public = False
            print("✅ Classified as PRIVATE university")
            break
        else:
            print("❌ Invalid input. Please enter 't', 'f', or 'q'")
    
    # Update all records for this university
    updated_count = 0
    for item in data:
        if item.get('university') == university:
            item['public_university'] = is_public
            updated_count += 1
    
    print(f"📝 Updated {updated_count} records for {university}")
    
    # Save progress after each university
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("💾 Progress saved to JSON file")

print("\n🎉 Classification completed!")

# Show final summary
public_count = sum(1 for item in data if item.get('public_university', False))
private_count = sum(1 for item in data if not item.get('public_university', False))
total_count = len(data)

print(f"\n📊 Final Summary:")
print(f"Total records: {total_count}")
print(f"Public universities: {public_count}")
print(f"Private universities: {private_count}")

# Show unique universities and their final classification
universities_final = {}
for item in data:
    if 'university' in item and item['university']:
        uni_name = item['university']
        is_public = item['public_university']
        universities_final[uni_name] = is_public

print(f"\n🏫 Final University Classification:")
for uni, is_public in sorted(universities_final.items()):
    status = "🏛️ Public" if is_public else "🏢 Private"
    print(f"- {uni}: {status}")

print(f"\n💾 All data saved to '{json_path}'")
print("🚀 You can now run your Streamlit app with the updated classification!")

# Save the updated JSON file
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Added 'public_university' field to all records in output_with_tuition.json")

# Show summary
public_count = sum(1 for item in data if item.get('public_university', False))
private_count = sum(1 for item in data if not item.get('public_university', False))
total_count = len(data)

print(f"\n📊 Summary:")
print(f"Total records: {total_count}")
print(f"Public universities: {public_count}")
print(f"Private universities: {private_count}")

# Show unique universities and their classification
universities = {}
for item in data:
    if 'university' in item and item['university']:
        uni_name = item['university']
        is_public = item['public_university']
        universities[uni_name] = is_public

print(f"\n🏫 University Classification:")
for uni, is_public in sorted(universities.items()):
    status = "Public" if is_public else "Private"
    print(f"- {uni}: {status}")
