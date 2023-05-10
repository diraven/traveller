package commands

import (
	"fmt"
	"log"

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
		if !state.State.IsOwner(i.Member.User.ID) {
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Flags: discordgo.MessageFlagsEphemeral,
					Embeds: []*discordgo.MessageEmbed{
						{
							Title:       "Ніт",
							Description: "Доступ заборонено.",
							Color:       15548997,
						},
					},
				},
			})
			return
		}

		// Convert options to map.
		options := i.ApplicationCommandData().Options
		optionMap := make(map[string]*discordgo.ApplicationCommandInteractionDataOption, len(options))
		for _, opt := range options {
			optionMap[opt.Name] = opt
		}

		// Prepare embed.
		user, err := s.User(optionMap["user_id"].StringValue())
		userName := ""
		if err != nil {
			userName = err.Error()
		} else {
			userName = user.Username + "#" + user.Discriminator + " (" + user.Mention() + ")"
		}
		embed := &discordgo.MessageEmbed{
			Title:       "Глобальний бан",
			Description: "",
			Fields: []*discordgo.MessageEmbedField{
				{Name: "Модератор", Value: i.Member.Mention(), Inline: true},
				{Name: "Користувач", Value: userName, Inline: true},
				{Name: "Ідентифікатор користувача", Value: optionMap["user_id"].StringValue(), Inline: true},
				{Name: "Причина", Value: optionMap["reason"].StringValue(), Inline: true},
			},
		}

		// Respond to interaction.
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseDeferredChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Content: "✅",
			},
		})

		// Distribute bans.
		successes := 0
		total := 0
		for guildId, tGuild := range state.State.ActiveGuilds() {
			total++
			_, err := s.State.Guild(guildId)
			if err != nil {
				log.Printf("%v (%v) %v", guildId, tGuild.Name, err)
				continue
			}
			err = s.GuildBanCreateWithReason(guildId, optionMap["user_id"].StringValue(), optionMap["reason"].StringValue(), 1)
			if err != nil {
				embed.Description = "**Помилка**: " + err.Error()
			} else {
				embed.Description = "**Статус**: видано"
				successes++
			}
			if tGuild.LogChannelId != "" {
				s.ChannelMessageSendEmbed(tGuild.LogChannelId, embed)
			}
		}

		// Respond to interaction.
		s.FollowupMessageCreate(i.Interaction, true, &discordgo.WebhookParams{
			Embeds: []*discordgo.MessageEmbed{
				{
					Title:       "Глобальний бан",
					Description: fmt.Sprintf("Видано на %d серверах з %d.", successes, total),
				},
			},
		})
	},
}
