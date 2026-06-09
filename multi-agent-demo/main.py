from workflows.sequential_flow import sequential_flow

topic = "The impact of artificial intelligence on society"

# Now 'result' will contain both pieces of data
result = sequential_flow(topic)

print("==============================")
print("📝 THE GENERATED ARTICLE (ANSWER):")
print("==============================")
print(result["generated_article"])

print("\n\n==============================")
print("🧐 THE REVIEWER FEEDBACK:")
print("==============================")
print(result["reviewer_feedback"])