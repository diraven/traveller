package publicroles

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"gitlab.com/diraven/crabot/utils"
)

var myCmd = &sugo.Command{
	Trigger:     "my",
	Description: "Lists all the public roles you are in.",
	HasParams:   true,
	Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
		// Make sure at least 3 symbols are provided in the query.
		if len(req.Query) < 3 && len(req.Query) > 0 {
			resp = req.NewResponse(sugo.ResponseWarning, "", "I need at least 3 symbols of the role name to look for one")
			return
		}

		// Get respective guild member.
		var m *discordgo.Member
		if m, err = req.Sugo.Session.GuildMember(req.Channel.GuildID, req.Message.Author.ID); err != nil {
			return
		}

		// Build a list of all member roles.
		var roles discordgo.Roles
		if roles, err = utils.RoleIDsToRoles(req, m.Roles); err != nil {
			return
		}

		// Filter out only public roles.
		if roles, _, err = publicRoles.filter(req, roles, req.Query); err != nil {
			return
		}

		// If user has no roles:
		if len(roles) == 0 {
			// Notify user about this.
			if req.Query == "" {
				resp = req.NewResponse(sugo.ResponseInfo, "", "you have no public roles")
			} else {
				resp = req.NewResponse(sugo.ResponseInfo, "", "you have no such public roles")
			}
			return
		}

		// Output roles we have found to the user.
		response := utils.FmtStringsSlice(utils.RolesToMentions(roles), ", ", "", 1500, " and more...", "")
		resp = req.NewResponse(sugo.ResponseInfo, "", response)

		return
	},
}
