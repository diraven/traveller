package commands

import (
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/state"
)

var cmdGBanUid = &Command{
	Definition: &discordgo.ApplicationCommand{
		Name:        "gban-id",
		Description: "Глобальний бан по ідентифікатору",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionString,
				Name:        "user_id",
				Description: "Ідентифікатор користувача",
				Required:    true,
			},
			{
				Type:        discordgo.ApplicationCommandOptionString,
				Name:        "reason",
				Description: "Причина бану",
				Required:    true,
			},
		},
	},
	Handler: func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		// Owners only.

		// Convert options to map.
		options := i.ApplicationCommandData().Options
		optionMap := make(map[string]*discordgo.ApplicationCommandInteractionDataOption, len(options))
		for _, opt := range options {
			optionMap[opt.Name] = opt
		}

		// Collect ban errors if any.
		errors := []string{}
		for guildId := range state.State.Guilds {
			err := s.GuildBanCreateWithReason(guildId, optionMap["user_id"].StringValue(), optionMap["reason"].StringValue(), 1)
			if err != nil {
				errors = append(errors, guildId+": "+err.Error())
			}
		}

		// Respond.
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{
					{
						Title:       "Глобальний бан: " + optionMap["user_id"].StringValue(),
						Description: strings.Join(errors, "\n"),
					},
				},
			},
		})
	},
}
