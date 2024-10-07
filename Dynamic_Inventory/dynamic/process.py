import json
import os
import sys

# Fonction pour générer l'inventaire Ansible à partir d'un fichier JSON
def generer_inventaire(json_file, noeud, groups):
    with open(json_file) as file:
        data = json.load(file)

    group_dict = {group: [] for group in groups}

    for host, details in data["_meta"]["hostvars"].items():
        if "kali-bastion" in host:
            continue  # Exclure les hôtes "kali" et "bastion"
        for group in groups:
            if group.lower() in details["proxmox_tags"]:
                group_dict[group].append(f"{host} ansible_host={host}")

    inventory = [f"[{noeud}]"]

    for group, hosts in group_dict.items():
        inventory.append(f"[{noeud}_{group}]")
        inventory.extend(hosts)
        inventory.append("")  # Ajouter une ligne vide entre les groupes

    inventory.append(f"[{noeud}:children]")
    inventory.extend([f"{noeud}_{group}" for group in groups])
    inventory.append("")

    return inventory, group_dict

def main():
    # Vérifier si un fichier JSON a été passé en argument
    if len(sys.argv) != 2:
        print("Usage: python script.py variables.json")
        sys.exit(1)

    variables_file = sys.argv[1]

    # Charger les variables depuis le fichier JSON
    with open(variables_file) as file:
        variables = json.load(file)

    nodes = variables["nodes"]
    groups = variables["groups"]

    all_inventory = []
    node_names = []

    # Générer les inventaires pour chaque fichier JSON
    for node in nodes:
        json_file = node["json_file"]
        noeud = node["noeud"]

        inventory, group_dict = generer_inventaire(json_file, noeud, groups)
        node_names.append(noeud)

        output_dir = f"../inventories/nodes/{noeud}"
        os.makedirs(output_dir, exist_ok=True)

        with open(os.path.join(output_dir, 'hosts'), 'w') as file:
            file.write("\n".join(inventory))

        os.makedirs(os.path.join(output_dir, 'group_vars'), exist_ok=True)

        for group, hosts in group_dict.items():
            with open(os.path.join(output_dir, f'group_vars/{group.lower()}.hosts'), 'w') as file:
                file.write("\n".join(hosts))

        all_inventory.extend(inventory)

    all_inventory.append("")
    all_inventory.append("[ALL:children]")
    all_inventory.extend(node_names)

    with open('../inventories/all.hosts', 'w') as file:
        file.write("\n".join(all_inventory))

    print("Ansible inventory files were successfully generated for all nodes and total inventory.")

if __name__ == "__main__":
    main()
