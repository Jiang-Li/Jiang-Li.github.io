# Analytics Flashcards

Interactive flashcard system for reviewing analytics concepts.

## Files

- `flashcards.html` - The main flashcard application
- `concepts.json` - The questions and answers data
- `README.md` - This documentation

## How to Edit Questions

To add, remove, or modify flashcard questions, edit the `concepts.json` file. Each question follows this format:

```json
{
    "question": "What is your question here?",
    "answer": "The detailed answer here."
}
```

### Adding a New Question

Add a new object to the array in `concepts.json`:

```json
{
    "question": "What is machine learning?",
    "answer": "A subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed."
}
```

### Removing a Question

Simply delete the entire question object (including the curly braces and comma).

### Modifying a Question

Edit the "question" or "answer" text directly in the JSON file.

## Important Notes

1. **JSON Format**: Make sure to maintain proper JSON formatting:
   - Use double quotes around strings
   - Include commas between objects (but not after the last one)
   - Proper bracket/brace matching

2. **Special Characters**: If you need to include quotes in your text, escape them with backslashes:
   ```json
   "answer": "This is called \"supervised learning\" in machine learning."
   ```

3. **Testing**: After making changes, reload the flashcards page to see your updates.

## Example Structure

```json
[
    {
        "question": "What is p-value?",
        "answer": "The probability that we observed our data, or data even more extreme, if the null hypothesis were true."
    },
    {
        "question": "What is Type 1 error?",
        "answer": "We reject the null hypothesis when it is actually true. The probability of Type 1 error is α (alpha)."
    }
]
```

## Usage

1. Open `flashcards.html` in a web browser
2. Click cards to flip them and see answers
3. Use the control buttons to:
   - **Flip All Cards**: Show all answers at once
   - **Reset All**: Hide all answers
   - **Shuffle**: Randomize the order of cards

The progress counter shows how many cards you've reviewed out of the total. 