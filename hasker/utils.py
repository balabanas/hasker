def read_env_file(env_file):
    env_vars = {}

    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and lines starting with '#'
            if not line or line.startswith('#'):
                continue

            # Split each line into key and value
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Add the key-value pair to the environment variables dictionary
            env_vars[key] = value

    return env_vars
