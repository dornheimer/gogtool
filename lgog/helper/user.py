def check_input(prompt, choices={'y', 'n'}):
    """Verify user input."""
    while True:
        choice = input(prompt)
        if choice.lower() in choices:
            break
        print(f'Invalid option: {choice}')

    return choice
