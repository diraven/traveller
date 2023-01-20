package commands

import (
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/state"
	"golang.org/x/exp/slices"
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
		if !slices.Contains(state.State.Owners, i.Member.User.ID) {
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
		}

		// Convert options to map.
		options := i.ApplicationCommandData().Options
		optionMap := make(map[string]*discordgo.ApplicationCommandInteractionDataOption, len(options))
		for _, opt := range options {
			optionMap[opt.Name] = opt
		}

		// Collect ban messages if any.
		messages := []string{}
		for guildId := range state.State.Guilds {
			guild, err := s.State.Guild(guildId)
			if err != nil {
				messages = append(messages, "Не можу знайти сервер: "+guildId)
			}
			err = s.GuildBanCreateWithReason(guildId, optionMap["user_id"].StringValue(), optionMap["reason"].StringValue(), 1)
			if err != nil {
				messages = append(messages, "**"+guild.Name+"**: "+err.Error())
			} else {
				messages = append(messages, "**"+guild.Name+"**: ✅")
			}
		}

		// Respond.
		user, err := s.User(optionMap["user_id"].StringValue())
		userName := ""
		if err != nil {
			userName = err.Error()
		} else {
			userName = user.Username + "#" + user.Discriminator + " (" + user.Mention() + ")"
		}
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{
					{
						Title:       "Глобальний бан",
						Description: strings.Join(messages, "\n"),
						Fields: []*discordgo.MessageEmbedField{
							{Name: "Користувач", Value: userName},
							{Name: "Ідентифікатор користувача", Value: optionMap["user_id"].StringValue()},
							{Name: "Причина", Value: optionMap["reason"].StringValue()},
						},
					},
				},
			},
		})
	},
}
