import subprocess

def run_terraform_command(command):
    """Exécute une commande Terraform et capture la sortie."""
    try:
        result = subprocess.run(
            command, 
            check=True, 
            text=True, 
            capture_output=True
        )
        print(f"Command Output: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None

def terraform_init():
    """Initialise Terraform."""
    print("Initializing Terraform...")
    return run_terraform_command(["terraform", "init"])

def terraform_init_upgrade():
    """Initialise Terraform."""
    print("Initializing Terraform...")
    return run_terraform_command(["terraform", "init", "-upgrade"])

def terraform_apply(skip_plan=False):
    """Applique le plan Terraform."""
    print("Applying Terraform configuration...")
    command = ["terraform", "apply"]
    
    if skip_plan:
        command.append("-auto-approve")  # Applique sans demander de confirmation
    
    return run_terraform_command(command)

def terraform_output():
    """Récupère et affiche les sorties Terraform."""
    print("Getting Terraform outputs...")
    return run_terraform_command(["terraform", "output"])
