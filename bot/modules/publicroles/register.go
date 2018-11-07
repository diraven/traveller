package publicroles

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"gitlab.com/diraven/crabot/bot/utils"
	"strings"
)

var registerCmd = &sugo.Command{
	Trigger:             "register",
	Description:         "Makes existing role public.",
	PermissionsRequired: discordgo.PermissionManageRoles,
	HasParams:           true,
	Execute: func(req *sugo.Request) (err error) {
		// Make sure at least 3 symbols are provided in the query.
		if len(req.Query) < 3 {
			_, err = req.NewResponse(sugo.ResponseWarning, "", "I need at least 3 symbols of the role name to look for one").Send()
			return
		}

		// Get guild.
		guild, err := req.GetGuild()
		if err != nil {
			return
		}

		// Get all guild roles.
		roles, err := req.Sugo.Session.GuildRoles(guild.ID)
		if err != nil {
			return
		}

		// Process request.
		var request string

		if len(req.Message.MentionRoles) > 0 {
			// If there is at least one role mention - we use that mention.
			request = req.Message.MentionRoles[0]
		} else {
			// Otherwise we just take full request.
			request = req.Query
		}

		// Make a storage for role we matched.
		var matchedRole *discordgo.Role

		// Try to find given role. Match must be exact (either ID or role name).
		for _, role := range roles {
			if strings.ToLower(role.Name) == strings.ToLower(request) || role.ID == request {
				if matchedRole != nil {
					_, err = req.NewResponse(sugo.ResponseWarning, "", "multiple roles found, try using role mention instead").Send()
					return
				}
				matchedRole = role
			}
		}

		// If we did not find any match:
		if matchedRole == nil {
			// Notify user about fail.
			_, err = req.NewResponse(sugo.ResponseWarning, "", "no roles with such name found").Send()
			return
		}

		// Try to find matched role among public ones:
		var fuzzy bool
		if roles, fuzzy, err = publicRoles.filter(req, guild.Roles, matchedRole.ID); err != nil {
			return
		}
		// If we have found non-fuzzy match:
		if len(roles) > 0 && !fuzzy {
			// Notify user that the role is already public.
			_, err = req.NewResponse(sugo.ResponseWarning, "", "this role is already public").Send()
			return
		}

		// Otherwise add new role to the public roles list.
		if err = publicRoles.register(req, matchedRole); err != nil {
			return
		}

		// And notify user about success.
		if _, err = req.NewResponse(sugo.ResponseSuccess, "", utils.RoleToMention(matchedRole)+" role is public now").Send(); err != nil {
			return
		}

		return
	},
}
