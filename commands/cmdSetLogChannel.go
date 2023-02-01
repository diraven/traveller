package commands

import (
	"fmt"

	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/state"
)

var defaultPermissions int64 = discordgo.PermissionBanMembers

var cmdSetLogChannel = &Command{
	Definition: &discordgo.ApplicationCommand{
		Name:                     "set-log-channel",
		Description:              "Обрати канал для повідомлень від бота.",
		DefaultMemberPermissions: &defaultPermissions,
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionChannel,
				Name:        "channel",
				Description: "Канал",
				Required:    true,
			},
		},
	},
	Handler: func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		// Convert options to map.
		options := i.ApplicationCommandData().Options
		optionMap := make(map[string]*discordgo.ApplicationCommandInteractionDataOption, len(options))
		for _, opt := range options {
			optionMap[opt.Name] = opt
		}

		// Set channel.
		_, ok := state.State.Guilds[i.GuildID]
		if !ok {
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Embeds: []*discordgo.MessageEmbed{
						{
							Description: fmt.Sprintf("Гільдію не знайдено: %v", i.GuildID),
						},
					},
				},
			})
			return
		}
		state.State.Guilds[i.GuildID].LogChannelId = optionMap["channel"].ChannelValue(s).ID
		state.State.Save()

		// Respond.
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{
					{
						Title:       "Налаштування каналу для логів",
						Description: fmt.Sprintf("Новий канал для логів: %s", optionMap["channel"].ChannelValue(s).Mention()),
					},
				},
			},
		})
	},
}
