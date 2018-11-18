package mod

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"gitlab.com/diraven/crabot/bot/utils"
	"strconv"
	"strings"
	"time"
)

var maxCount = 100 // Maximum amount of messages deleted.

// Module to handle messages cleanup from the channel.
var clear = &sugo.Command{
	Trigger: "clear",
	Description: fmt.Sprintf("Deletes last few messages (up to %d in one go).\n", maxCount) +
		"**Example:** `clean @user 15` will delete last 15 messages in the channel by user @user\n" +
		"**Example:** `clean 15` will delete last 15 messages in the channel\n" +
		"**Example:** `clean @user` will delete last 100 messages in the channel by @user\n" +
		"",
	HasParams:           true,
	PermissionsRequired: discordgo.PermissionManageMessages,
	Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
		// Command has to have 1 or 2 parameters.
		ss := strings.Split(req.Query, " ")

		var batchSize = 100  // Amount of messages to get in one go.
		var userID string    // UserID to delete messages for.
		var count = maxCount // Default amount of messages to be deleted.

		switch len(ss) {
		case 1: // Means we have got either user mention or amount of messages to delete.
			if ss[0] == "" { // No parameters given.
				_, err = req.NewResponse(sugo.ResponseWarning, "", "not sure what messages to delete... can you give more info, please? see help for details").Send()
				return
			}

			if len(req.Message.Mentions) > 0 { // Get user mention if available.
				// Get user id.
				userID = req.Message.Mentions[0].ID
			} else { // Get amount of messages to delete.
				// Try to parse count.
				if count, err = strconv.Atoi(ss[0]); err != nil {
					return
				}
			}
			break
		case 2: // Means we've got both user mention and amount of messages to delete.
			if len(req.Message.Mentions) == 0 { // Query must have mention.
				_, err = req.NewResponse(sugo.ResponseWarning, "", "unable to find a mention of the person to delete messages from").Send()
				return

			}
			userID = req.Message.Mentions[0].ID

			// Try to get count of messages to delete.
			count, err = strconv.Atoi(ss[0]) // Try first argument.

			if err != nil { // If first argument did not work.
				count, err = strconv.Atoi(ss[1]) // Try second one.
				if err != nil {
					_, err = req.NewResponse(sugo.ResponseWarning, "", "unable to find count of messages to delete").Send()
					return
				}
			}
			break
		default:
			_, err = req.NewResponse(sugo.ResponseWarning, "", "unable to understand what needs to be done, sorry... see help for details").Send()
			return

		}

		// Validate count.
		if count > maxCount {
			_, err = req.NewResponse(sugo.ResponseWarning, "", "too many messages to delete, I don't think I can handle that many, try less or equal then "+strconv.Itoa(maxCount)).Send()
			return

		}

		lastMessageID := req.Message.ID      // To store last message id.
		var tmpMessages []*discordgo.Message // To store 100 current messages that are being scanned.
		var messageIDs []string              // Resulting slice of messages to  be deleted.
		limit := batchSize                   // Default limit per batch.

		if userID == "" && count < batchSize { // If user ID is not specified - we retrieve and delete exact count of messages specified.
			limit = count
		}

		// Start getting messages.
	messageLoop:
		for {
			// Get next 100 messages.
			if tmpMessages, err = req.Sugo.Session.ChannelMessages(req.Channel.ID, limit, lastMessageID, "", ""); err != nil {
				return
			}

			// For each message.
			for _, message := range tmpMessages {
				// Get message creation date.
				var then time.Time
				if then, err = utils.DiscordTimestampToTime(string(message.Timestamp)); err != nil {
					return
				}

				if time.Since(then).Hours() >= 24*14 {
					// We are unable to delete messages older then 14 days.
					_, err = req.NewResponse(sugo.ResponseWarning, "", "unable to delete messages older then 2 weeks (discord does not allow me to do that)").Send()
					return
				}
				if userID != "" {
					// If user ID is specified, we compare message with the user ID.
					if message.Author.ID == userID {
						messageIDs = append(messageIDs, message.ID)
					}
				} else {
					// Otherwise just add message ID to the list for deletion.
					messageIDs = append(messageIDs, message.ID)
				}

				// If we have enough messages staged for deletion.
				if len(messageIDs) >= count {
					// Finish looking for messages.
					break messageLoop
				}

			}

			if len(tmpMessages) < batchSize {
				break messageLoop // We have no messages left to scan.
			}

			if len(tmpMessages) == batchSize {
				lastMessageID = tmpMessages[batchSize-1].ID // Next time start scanning from the message specified.
			}
		}

		// Delete command itself. Ignore errors (such as message already deleted by someone) for now.
		_ = req.Sugo.Session.ChannelMessageDelete(req.Channel.ID, req.Message.ID)

		// Perform selected messages deletion. Ignore errors (such as message already deleted by someone) for now.
		_ = req.Sugo.Session.ChannelMessagesBulkDelete(req.Channel.ID, messageIDs)

		// Notify user about deletion.
		if err = req.AddReaction(sugo.ReactionOk); err != nil {
			return
		}

		return
	},
}
