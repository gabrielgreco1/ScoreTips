import * as cheerio from 'cheerio';

export class PlayerStatsExtractor {
    extractPlayerStats(html) {
        const $ = cheerio.load(html);
        const playersStats = {};

        $('div.table_container').each((tableIndex, table) => {
            const captionText = $(table).find('caption').text();

            if (captionText.includes('Estatísticas de goleiro')) {
                // Tabela de goleiros
                $(table).find('table.stats_table tbody tr').each((index, row) => {
                    const playerName = $(row).find('[data-stat="player"]').text().trim();

                    if (!playerName) {
                        console.log('Nome do jogador não encontrado na linha:', index);
                        return;
                    }

                    const goalkeeperStats = this.mapGoalkeeperStats($, row);
                    // console.log(`Estatísticas de ${playerName} (Goleiro):`, goalkeeperStats);

                    playersStats[playerName] = {
                        ...playersStats[playerName],
                        ...goalkeeperStats
                    };
                });
            } else if (captionText.includes('Estatísticas do jogador')) {
                // Tabela de jogadores de linha
                const teamName = this.getTeamNameFromCaption(captionText);

                if (!teamName) {
                    console.log('Nome do time não encontrado na legenda:', captionText);
                    return;
                }

                $(table).find('table.stats_table tbody tr').each((index, row) => {
                    const playerName = $(row).find('[data-stat="player"]').text().trim();
                    const position = $(row).find('[data-stat="position"]').text().trim();

                    if (!playerName) {
                        console.log('Nome do jogador não encontrado na linha:', index);
                        return;
                    }

                    if (!playersStats[playerName]) {
                        playersStats[playerName] = this.initializePlayerStats($, row, teamName, playerName, position);
                    }
                });
            }
        });

        return Object.values(playersStats);
    }

    getTeamNameFromCaption(captionText) {
        const teamName = captionText.split(' Estatísticas do jogador')[0].trim();
        return teamName || null;
    }

    initializePlayerStats($, row, teamName, playerName, position) {
        return {
            name: playerName,
            team: teamName,
            shirtNumber: $(row).find('[data-stat="shirtnumber"]').text().trim() || "N/A",
            nationality: $(row).find('[data-stat="nationality"]').text().trim().slice(-3, -1) || "N/A",
            position: position,
            age: $(row).find('[data-stat="age"]').text().trim() || "N/A",
            minutes: $(row).find('[data-stat="minutes"]').text().trim() || "0",
            goals: $(row).find('[data-stat="goals"]').text().trim() || "0",
            assists: $(row).find('[data-stat="assists"]').text().trim() || "0",
            penaltiesMade: $(row).find('[data-stat="pens_made"]').text().trim() || "0",
            penaltiesAttempted: $(row).find('[data-stat="pens_att"]').text().trim() || "0",
            totalShots: $(row).find('[data-stat="shots"]').text().trim() || "0",
            shotsOnTarget: $(row).find('[data-stat="shots_on_target"]').text().trim() || "0",
            yellowCards: $(row).find('[data-stat="cards_yellow"]').text().trim() || "0",
            redCards: $(row).find('[data-stat="cards_red"]').text().trim() || "0",
            touches: $(row).find('[data-stat="touches"]').text().trim() || "0",
            tackles: $(row).find('[data-stat="tackles"]').text().trim() || "0",
            interceptions: $(row).find('[data-stat="interceptions"]').text().trim() || "0",
            blocks: $(row).find('[data-stat="blocks"]').text().trim() || "0",
            xG: $(row).find('[data-stat="xg"]').text().trim() || "0.0",
            npxG: $(row).find('[data-stat="npxg"]').text().trim() || "0.0",
            xAG: $(row).find('[data-stat="xg_assist"]').text().trim() || "0.0",
            sca: $(row).find('[data-stat="sca"]').text().trim() || "0",
            gca: $(row).find('[data-stat="gca"]').text().trim() || "0",
            passesCompleted: $(row).find('[data-stat="passes_completed"]').text().trim() || "0",
            passesAttempted: $(row).find('[data-stat="passes"]').text().trim() || "0",
            passCompletionPercentage: $(row).find('[data-stat="passes_pct"]').text().trim() || "0",
            progressivePasses: $(row).find('[data-stat="progressive_passes"]').text().trim() || "0",
            carries: $(row).find('[data-stat="carries"]').text().trim() || "0",
            progressiveCarries: $(row).find('[data-stat="progressive_carries"]').text().trim() || "0",
            takeOns: $(row).find('[data-stat="take_ons"]').text().trim() || "0",
            takeOnsWon: $(row).find('[data-stat="take_ons_won"]').text().trim() || "0"

        };
    }

    mapGoalkeeperStats($, row) {
        return {
            shotsOnTargetAgainst: $(row).find('[data-stat="gk_shots_on_target_against"]').text().trim() || "0",
            goalsConceded: $(row).find('[data-stat="gk_goals_against"]').text().trim() || "0",
            saves: $(row).find('[data-stat="gk_saves"]').text().trim() || "0",
            savePercentage: $(row).find('[data-stat="gk_save_pct"]').text().trim() || "0.0",
            psxg: $(row).find('[data-stat="gk_psxg"]').text().trim() || "0.0",
            passesLaunched: $(row).find('[data-stat="gk_passes_launched"]').text().trim() || "0",
            passesLaunchedAccuracy: $(row).find('[data-stat="gk_passes_pct_launched"]').text().trim() || "0.0",
            throws: $(row).find('[data-stat="gk_passes_throws"]').text().trim() || "0",
            goalKicks: $(row).find('[data-stat="gk_goal_kicks"]').text().trim() || "0",
            crossesFaced: $(row).find('[data-stat="gk_crosses"]').text().trim() || "0",
            sweeperActions: $(row).find('[data-stat="gk_def_actions_outside_pen_area"]').text().trim() || "0",
            sweeperDistance: $(row).find('[data-stat="gk_avg_distance_def_actions"]').text().trim() || "0.0"
        };
    }
}
