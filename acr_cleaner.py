import streamlit as st
import subprocess
import json

# Função para obter os Azure Container Registries disponíveis
def get_acrs():
    command = "az acr list --output json"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    acrs = json.loads(result.stdout)
    return acrs

# Função para obter os repositórios
def get_repositories(acr_name):
    command = f"az acr repository list --name {acr_name} --output json"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return json.loads(result.stdout)

# Função para obter as tags de um repositório
def get_tags(acr_name, repository):
    command = f"az acr repository show-tags --name {acr_name} --repository {repository} --orderby time_desc --output json"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return json.loads(result.stdout)

# Função para deletar tags antigas
def delete_tags(acr_name, repository, tags_to_keep):
    tags = get_tags(acr_name, repository)
    if len(tags) > tags_to_keep:
        tags_to_delete = tags[tags_to_keep:]
        for tag in tags_to_delete:
            command = f"az acr repository delete --name {acr_name} --image {repository}:{tag} --yes"
            subprocess.run(command, shell=True)
            st.write(f"Deleted {repository}:{tag}")
    else:
        st.write(f"No tags to delete for {repository}")

# Streamlit UI
st.title("Azure Container Registry Cleaner")

# Listar os ACRs disponíveis
acrs = get_acrs()
if acrs:
    acr_names = [acr['name'] for acr in acrs]
    selected_acrs = st.multiselect("Selecione os Azure Container Registries para limpeza:", acr_names)

    # Input do usuário para o número de tags a manter
    tags_to_keep = st.number_input("Número de tags recentes a manter:", min_value=1, value=3, step=1)

    # Executar a limpeza para cada ACR selecionado
    if selected_acrs and st.button("Executar Limpeza"):
        for acr_name in selected_acrs:
            repositories = get_repositories(acr_name)
            for repo in repositories:
                st.write(f"Repositório: {repo}")
                tags = get_tags(acr_name, repo)
                st.write(f"Tags disponíveis: {tags}")
                if len(tags) > tags_to_keep:
                    st.write(f"Tags a serem deletadas: {tags[tags_to_keep:]}")
                    delete_tags(acr_name, repo, tags_to_keep)
                else:
                    st.write(f"Nada a deletar para {repo}")

        st.write("Operação concluída!")

    # Checkbox para selecionar repositórios manualmente
    manual_selection = st.checkbox("Seleção Manual")
    if manual_selection:
        for acr_name in selected_acrs:
            repositories = get_repositories(acr_name)
            for repo in repositories:
                tags = get_tags(acr_name, repo)
                selected_tags = st.multiselect(f"Selecione as tags para manter em {repo}:", tags, default=tags[:tags_to_keep])
                if st.button(f"Aplicar Seleção para {repo}"):
                    tags_to_delete = [tag for tag in tags if tag not in selected_tags]
                    for tag in tags_to_delete:
                        command = f"az acr repository delete --name {acr_name} --image {repo}:{tag} --yes"
                        subprocess.run(command, shell=True)
                        st.write(f"Deleted {repo}:{tag}")

else:
    st.write("Nenhum Azure Container Registry encontrado.")