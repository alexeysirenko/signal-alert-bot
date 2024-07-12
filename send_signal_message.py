import subprocess
import yaml


def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


def is_registered(phone_number):
    try:
        result = subprocess.run([
            'signal-cli', '-u', phone_number, 'listAccounts'
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def register_phone_number(phone_number):
    try:
        subprocess.run([
            'signal-cli', '-u', phone_number, 'register'
        ], check=True)
        print(f"Verification code sent to {phone_number}. Please enter the code:")
        verification_code = input("Verification code: ")
        subprocess.run([
            'signal-cli', '-u', phone_number, 'verify', verification_code
        ], check=True)
        print("Phone number registered successfully")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during registration: {e}")


def send_signal_message(config, message, recipient=None, group=None):
    phone_number = config['signal']['phone']

    if not is_registered(phone_number):
        print(f"{phone_number} is not registered. Registering now...")
        register_phone_number(phone_number)

    command = ['signal-cli', '-u', phone_number, 'send', '-m', message]

    if recipient:
        command.append(recipient)
    elif group:
        command.extend(['-g', group])
    else:
        raise ValueError("Either recipient or group must be specified")

    try:
        subprocess.run(command, check=True)
        print(f"Message {message} sent successfully to {recipient or group}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    config = load_config('config.yaml')
    group_id = config['signal']['group_id']  # Replace with your actual group ID
    message_to_send = config['signal']['message_on_no_alert']

    send_signal_message(config, message_to_send, group=group_id)
