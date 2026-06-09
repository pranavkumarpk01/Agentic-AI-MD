import ollama

print("===================================")
print(" LOCAL AI WORKFLOW AGENT ")
print("===================================")

# User Input
user_input = input("\nEnter text to summarize:\n\n")

print("\nAI Agent is thinking...\n")

# Better Prompt Engineering
response = ollama.chat(
    model='llama3.2:3b ',
    messages=[
        {
            'role': 'system',
            'content': '''
You are an expert summarization AI.

Your task:
- Create a SHORT summary
- Keep only important points
- Reduce the content length significantly
- Do NOT repeat the original text
- Return only the summary
- Maximum 1 lines
'''
        },
        {
            'role': 'user',
            'content': user_input
        }
    ]
)

# Extract summary
summary = response['message']['content']

# Save to file
with open("summary.txt", "w") as file:
    file.write(summary)

print("========== AI SUMMARY ==========\n")
print(summary)

print("\n===================================")
print(" Summary saved to summary.txt ")
print("===================================")