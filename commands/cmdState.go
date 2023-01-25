package commands

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/state"
)

var cmdState = &Command{
	Definition: &discordgo.ApplicationCommand{
		Name:        "state",
		Description: "Управління даними",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionSubCommand,
				Name:        "load",
				Description: "Завантажити дані з втратою поточних",
			},
			{
				Type:        discordgo.ApplicationCommandOptionSubCommand,
				Name:        "save",
				Description: "Зберегти поточні дані на диск",
			},
		},
	},
	Handler: func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		// Owners only.
		if !state.State.IsOwner(i.Member.User.ID) {
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Embeds: []*discordgo.MessageEmbed{
						{
							Title:       "Ніт",
							Description: "Доступ заборонено.",
						},
					},
				},
			})
			return
		}

		var embed *discordgo.MessageEmbed

		switch i.ApplicationCommandData().Options[0].Name {
		case "load":
			state.State.Load()
			embed = &discordgo.MessageEmbed{
				Title:       "Перечитування даних з диску",
				Description: "Успішно.",
			}

		case "save":
			state.State.Save()
			embed = &discordgo.MessageEmbed{
				Title:       "Запис даних на диск",
				Description: "Успішно.",
			}

		}

		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
			},
		})
	},
}
