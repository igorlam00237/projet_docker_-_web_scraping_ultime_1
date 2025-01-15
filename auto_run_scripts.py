import subprocess
import time
import pymysql

def execute_command(command, cwd=None):
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, text=True, capture_output=True)
        print(f"Command '{command}' executed successfully.")
        print(f"Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error while executing command: {command}")
        print(f"Error message: {e.stderr}")
        exit(1)

def wait_for_mysql(host, user, password, database, port=3307, retries=10, delay=5):
    """Wait until MySQL is ready."""
    for attempt in range(retries):
        try:
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            connection.close()
            print("MySQL is ready!")
            return
        except pymysql.MySQLError as e:
            print(f"Attempt {attempt + 1}/{retries} - MySQL not ready yet. Retrying in {delay} seconds...")
            time.sleep(delay)
    print("MySQL is not ready after several attempts. Exiting...")
    exit(1)

# Command 1: Start Docker containers
execute_command("docker compose up --build -d")

# Wait for MySQL to be ready (adjust the host, user, password, and database as needed)
wait_for_mysql(
    host="127.0.0.1",   # Or the Docker service name, e.g., "mysql_container"
    user="root",
    password="password",
    database="scrapy_db"
)

# Command 2: Run spiders
working_directory = "watch_comp"
execute_command("python run_spiders.py", cwd=working_directory)
