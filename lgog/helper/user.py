def check_input(prompt, choices={'y', 'n'}):
    """Verify user input."""
    prompt += " (y/n) "
    while True:
        choice = input(prompt)
        if choice.lower() in choices:
            break
        print(f'Invalid option: {choice}')

    return choice
