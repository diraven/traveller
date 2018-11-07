package publicroles

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"gitlab.com/diraven/crabot/bot/utils"
)

var whoCmd = &sugo.Command{
	Trigger:     "who",
	Description: "Lists people that have public role specified.",
	HasParams:   true,
	Execute: func(req *sugo.Request) (err error) {
		// Make sure at least 3 symbols are provided in the query.
		if len(req.Query) < 3 {
			_, err = req.NewResponse(sugo.ResponseWarning, "", "I need at least 3 symbols of the role name to look for one").Send()
			return
		}

		// Get guild.
		var guild *discordgo.Guild
		if guild, err = req.GetGuild(); err != nil {
			return
		}

		// Try to filter role based on query.
		var roles discordgo.Roles
		if roles, _, err = publicRoles.filter(req, guild.Roles, req.Query); err != nil {
			return
		}
		if len(roles) == 0 {
			_, err = req.NewResponse(sugo.ResponseWarning, "", "no public roles found with such name").Send()
			return
		}
		if len(roles) > 1 {
			// TODO: better display what exactly roles were found
			_, err = req.NewResponse(sugo.ResponseWarning, "", "multiple public roles found: ").Send()
			return
		}
		var requestedRole *discordgo.Role
		requestedRole = roles[0]

		// Make members array we will be working with.
		var memberMentions []string
		for _, member := range guild.Members {
			for _, roleID := range member.Roles {
				if roleID == requestedRole.ID {
					memberMentions = append(memberMentions, member.User.Mention())
				}
			}
		}

		// If no one has this role:
		if len(memberMentions) == 0 {
			_, err = req.NewResponse(
				sugo.ResponseInfo,
				"",
				"no one has the "+utils.RoleToMention(requestedRole)+" role (yet?)",
			).Send()
			return
		}

		// Start building response.
		response := utils.FmtStringsSlice(memberMentions, ", ", "", 1500, ", and more...", "")

		// Send response.
		if _, err = req.NewResponse(sugo.ResponseInfo, "", "people with "+utils.RoleToMention(requestedRole)+" role:\n\n"+response).Send(); err != nil {
			return
		}

		return
	},
}
