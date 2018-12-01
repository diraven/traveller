package main

import (
	"context"
	"database/sql"
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"github.com/pkg/errors"
	"github.com/volatiletech/sqlboiler/boil"
	"github.com/volatiletech/sqlboiler/queries/qm"
	"gitlab.com/diraven/crabot/models"
	"strings"
)

func isTriggeredFactory(db *sql.DB) (isTriggered func(req *sugo.Request) (triggered bool)) {
	return func(req *sugo.Request) (triggered bool) {
		// Check channel type:
		if req.Channel.Type == discordgo.ChannelTypeDM {
			// It's Direct Messaging Channel. Every message here is in fact a direct message to the bot, so we consider
			// it to be command without any further checks for prefixes.

			// Nevertheless, also remember to remove default bot command prefix if any.
			req.Query = strings.Replace(req.Query, req.Sugo.DefaultTrigger, req.Sugo.Self.Mention(), 1)

			triggered = true
			return
		} else if req.Channel.Type == discordgo.ChannelTypeGuildText || req.Channel.Type == discordgo.ChannelTypeGroupDM {
			// It's either Guild Text Channel or multiple people direct group Channel.
			// In order to detect command we need to check for bot Trigger.

			// Check for guild specific trigger.
			var dbGuild *models.MydiscordGuild
			var guild *discordgo.Guild

			// Get guild from the request.
			var err error
			guild, err = req.GetGuild()
			if err != nil {
				req.Sugo.HandleError(req, errors.Wrap(err, "unable to get discord guild"))
				return
			}

			// Try to get guild from the database.
			var dbGuilds models.MydiscordGuildSlice
			dbGuilds, err = models.MydiscordGuilds(qm.Where("discord_id = ?", guild.ID)).All(context.TODO(), db)
			if err != nil {
				req.Sugo.HandleError(req, errors.Wrap(err, "unable to retrieve guild from the db"))
				return
			}

			if len(dbGuilds) > 0 {
				// If guild was found:
				dbGuild = dbGuilds[0]
			} else {
				// Guild not found. Initialize it.
				dbGuild = &models.MydiscordGuild{
					DiscordID: guild.ID,
					Name:      guild.Name,
					Trigger:   req.Sugo.DefaultTrigger,
				}

				// Add guild to the DB.
				err = dbGuild.Insert(context.TODO(), db, boil.Infer())
				if err != nil {
					req.Sugo.HandleError(req, errors.Wrap(err, "unable to save guild to the db"))
					return
				}
			}

			// If DB trigger is set - replace db guild's prefix with bot mention for it to be detected.
			if dbGuild.Trigger != "" && strings.HasPrefix(req.Query, dbGuild.Trigger) {
				req.Query = strings.Replace(req.Query, dbGuild.Trigger, req.Sugo.Self.Mention(), 1)
			}

			// If bot nick was changed on the server - it will have ! in it's mention, so we need to remove that in order
			// for mention detection to work right.
			if strings.HasPrefix(req.Query, "<@!") {
				req.Query = strings.Replace(req.Query, "<@!", "<@", 1)
			}

			// If the message starts with bot mention:
			if strings.HasPrefix(strings.TrimSpace(req.Query), req.Sugo.Self.Mention()) {
				// Remove bot Trigger from the string.
				req.Query = strings.TrimSpace(strings.TrimPrefix(req.Query, req.Sugo.Self.Mention()))
				// Bot is triggered.
				triggered = true
				return
			}

			// Otherwise bot is not triggered.
			return
		}

		// We ignore all other channel types and consider bot not triggered.
		return
	}
}
