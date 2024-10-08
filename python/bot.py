from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import token
import requests
import os

# API endpoint da sua aplicação Flask
API_URL = "http://localhost:5000"

# Função inicial do comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Comparação de Times", callback_data="comparison")],
        [InlineKeyboardButton("Probabilidades de Jogadores", callback_data="player_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Escolha o tipo de probabilidade:', reply_markup=reply_markup)
    context.user_data['step'] = 'select_type'


# Função que lida com as interações dos botões
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    step = context.user_data.get('step', '')

    # Seleção do tipo de probabilidade (times ou jogadores)
    if step == 'select_type':
        if query.data == 'comparison':  # Comparação de times
            context.user_data['type'] = 'comparison'
            response = requests.get(f"{API_URL}/list_countries")
            countries = response.json() if response.status_code == 200 else []

            if countries:
                keyboard = [[InlineKeyboardButton(country, callback_data=country)] for country in countries]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text('Escolha o país:', reply_markup=reply_markup)
                context.user_data['step'] = 'select_country_comparison'
            else:
                await query.edit_message_text('Erro ao buscar os países.')

        elif query.data == 'player_stats':  # Probabilidades de jogadores
            context.user_data['type'] = 'player_stats'
            response = requests.get(f"{API_URL}/list_countries")
            countries = response.json() if response.status_code == 200 else []

            if countries:
                keyboard = [[InlineKeyboardButton(country, callback_data=country)] for country in countries]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text('Escolha o país:', reply_markup=reply_markup)
                context.user_data['step'] = 'select_country_player'
            else:
                await query.edit_message_text('Erro ao buscar os países.')

    # Seleção do país para comparação de times
    elif step == 'select_country_comparison':
        selected_country = query.data
        context.user_data['country'] = selected_country

        response = requests.get(f"{API_URL}/list_championships?country={selected_country}")
        championships = response.json() if response.status_code == 200 else []

        if championships:
            filtered_championships = [' '.join(champ.rsplit('_', 1)) for champ in championships if champ.startswith(f"{selected_country}_")]            

            filtered_championships = sorted(filtered_championships)


            keyboard = [
                [InlineKeyboardButton(champ.split('_', 1)[1], callback_data=champ)] for champ in filtered_championships
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Selecione o campeonato:', reply_markup=reply_markup)
            context.user_data['step'] = 'select_championship_comparison'
        else:
            await query.edit_message_text(f"Erro ao buscar os campeonatos para o país {selected_country}.")

    # Seleção do país para probabilidades de jogadores
    elif step == 'select_country_player':
        selected_country = query.data
        context.user_data['country'] = selected_country

        response = requests.get(f"{API_URL}/list_championships?country={selected_country}")
        championships = response.json() if response.status_code == 200 else []

        if championships:
            filtered_championships = [champ for champ in championships if champ.startswith(f"{selected_country}_")]

            # Mostrar os nomes dos campeonatos sem o prefixo do país
            keyboard = [
                [InlineKeyboardButton(champ.split('_', 1)[1], callback_data=champ)] for champ in filtered_championships
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Selecione o campeonato:', reply_markup=reply_markup)
            context.user_data['step'] = 'select_championship_player'
        else:
            await query.edit_message_text(f"Erro ao buscar os campeonatos para o país {selected_country}.")

    # Seleção do campeonato para comparação de times
    elif step == 'select_championship_comparison':
        selected_championship = query.data
        context.user_data['championship'] = selected_championship

        # Buscar os times do campeonato
        response = requests.get(f"{API_URL}/list_teams?collection={selected_championship}")
        teams = response.json() if response.status_code == 200 else []

        if teams:
            message = f"Você escolheu o campeonato: {selected_championship.split('_', 1)[1]}. Agora, selecione o primeiro time:"
            context.user_data['teams'] = teams  # Armazena os times na user_data
            await show_teams(query, context, teams, message)
            context.user_data['step'] = 'select_first_team'
        else:
            await query.edit_message_text(f"Erro ao buscar os times para o campeonato {selected_championship}.")

    # Seleção do campeonato para jogadores
    elif step == 'select_championship_player':
        selected_championship = query.data
        context.user_data['championship'] = selected_championship

        # Buscar os times do campeonato
        response = requests.get(f"{API_URL}/list_teams?collection={selected_championship}")
        teams = response.json() if response.status_code == 200 else []

        if teams:
            message = f"Você escolheu o campeonato: {selected_championship.split('_', 1)[1]}. Agora, selecione o time para ver os jogadores:"
            await show_teams(query, context, teams, message)
            context.user_data['step'] = 'select_team_for_player'
        else:
            await query.edit_message_text(f"Erro ao buscar os times para o campeonato {selected_championship}.")

    # Seleção do primeiro time para comparação de times
    elif step == 'select_first_team':
        selected_team = query.data
        context.user_data['team1'] = selected_team  # Salva o time selecionado

        teams = context.user_data.get('teams', [])  # Recupera os times da user_data

        message = f"Você escolheu o time {selected_team}. Agora, selecione o segundo time:"
        await show_teams(query, context, teams, message)
        context.user_data['step'] = 'select_second_team'

    # Seleção do segundo time para comparação
    elif step == 'select_second_team':
        selected_team = query.data
        context.user_data['team2'] = selected_team  # Salva o time selecionado

        await query.edit_message_text(f"Você escolheu o time {context.user_data['team1']} e {context.user_data['team2']}. Gerando PDF...")

        # Gerar o PDF chamando a API
        pdf_filename = await generate_pdf(context.user_data['team1'], context.user_data['team2'], context.user_data['championship'])

        if pdf_filename:
            await context.bot.send_document(chat_id=query.message.chat_id, document=open(pdf_filename, 'rb'))
            os.remove(pdf_filename)  # Remover o arquivo local após o envio
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Erro ao gerar o PDF.")

    # Seleção do time para jogadores
    elif step == 'select_team_for_player':
        selected_team = query.data
        context.user_data['team_name'] = selected_team

        # Busca os jogadores do time automaticamente
        players = await get_players_from_team(selected_team, context.user_data['championship'])

        if players:
            message = f"Você escolheu o time: {selected_team}. Agora, selecione o jogador:"
            await show_teams(query, context, players, message)
            context.user_data['step'] = 'select_player'
        else:
            await query.edit_message_text(f"Não foram encontrados jogadores para o time {selected_team}.")

    # Seleção do jogador e geração do PDF
    elif step == 'select_player':
        selected_player = query.data
        context.user_data['player_name'] = selected_player

        await query.edit_message_text(f"Você escolheu o jogador {selected_player}. Gerando PDF...")

        # Gerar o PDF chamando a API
        pdf_filename = await generate_player_pdf(context.user_data['team_name'], context.user_data['player_name'], context.user_data['championship'])

        if pdf_filename:
            await context.bot.send_document(chat_id=query.message.chat_id, document=open(pdf_filename, 'rb'))
            os.remove(pdf_filename)
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Erro ao gerar o PDF.")


# Função para buscar os jogadores do time automaticamente
async def get_players_from_team(team_name, championship):
    try:
        response = requests.get(f"{API_URL}/get_players?team={team_name}&collection={championship}")
        if response.status_code == 200:
            team_data = response.json()
            players = team_data.get('players', [])  # Obtém a lista de jogadores do JSON
            return players
        else:
            return None
    except Exception as e:
        print(f"Erro ao buscar jogadores: {e}")
        return None


# Função para gerar PDF com estatísticas de comparação de times
async def generate_pdf(team1, team2, championship):
    try:
        response = requests.get(f"{API_URL}/generate_pdf?team1={team1}&team2={team2}&collection={championship}")
        if response.status_code == 200:
            filename = f"{team1}_vs_{team2}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        else:
            return None
    except Exception as e:
        print(f"Erro ao chamar a API: {e}")
        return None


# Função para gerar PDF com estatísticas de jogadores
async def generate_player_pdf(team_name, player_name, championship):
    try:
        response = requests.get(f"{API_URL}/generate_pdf_player?team={team_name}&player={player_name}&collection={championship}")
        if response.status_code == 200:
            filename = f"{team_name}_{player_name}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        else:
            return None
    except Exception as e:
        print(f"Erro ao chamar a API: {e}")
        return None


# Função para exibir times ou jogadores em várias linhas de botões
async def show_teams(update, context, items, message):
    chunks = chunk_list(items, 4)
    keyboard = [[InlineKeyboardButton(item, callback_data=item) for item in chunk] for chunk in chunks]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)


# Função para dividir listas em pedaços
def chunk_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


# Função principal
if __name__ == '__main__':
    TOKEN = token
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot rodando...")
    app.run_polling()
