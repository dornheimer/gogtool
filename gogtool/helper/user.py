"""Functions that handle user interaction."""

from gogtool.helper.log import logger


def confirm(prompt, default=False):
    """Ask user to confirm with 'y' or 'n' (or equivalent responses).

    Note:
        Valid responses are: 'y', 'n', 'yes', 'no', '1', '0', 'true', 'false'

    :param prompt: Question that requires user confirmation.
    :param default: Default value if user fails to respond.
    """
    logger.info("Asking user for confirmation")
    responses_true = ["y", "yes", "1", "true"]
    responses_false = ["n", "no", "0", "false"]
    responses = responses_true + responses_false
    prompt += " (y/n) "

    res = verify_response(prompt, responses)
    if res is not None:
        value = res in responses_true
    else:
        value = default

    logger.debug(f"User confirmation: {value}")
    return value


def verify_response(prompt, reponses, attempts=3):
    """Verify user response.

    :param prompt: Prompt as passed in from user.confirm().
    :param responses: List of valid user responses to the prompt.
    :param attempts: Number of attempts to get valid user response.
        (default = 3)
    """
    logger.debug(f"Valid reponses are: {', '.join(reponses)}")
    for attempt in range(attempts):
        res = input(prompt).lower()
        if res in reponses:
            logger.debug(f"User response for {prompt}: {res}")
            return res
        print(f'Invalid option: {res}')

    print("No choice was made.")
    logger.debug(f"Failed to get valid user response: {prompt}")
    return None
