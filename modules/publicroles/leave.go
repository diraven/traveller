package publicroles

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"github.com/pkg/errors"
	"gitlab.com/diraven/crabot/utils"
)

var leaveCmd = &sugo.Command{
	Trigger:     "leave",
	Description: "Removes person to the public role.",
	HasParams:   true,
	Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
		// Make sure at least 3 symbols are provided in the query.
		if len(req.Query) < 3 {
			resp = req.NewResponse(sugo.ResponseWarning, "", "I need at least 3 symbols of the role name to look for one")
			return
		}

		// Get guild.
		var guild *discordgo.Guild
		if guild, err = req.GetGuild(); err != nil {
			return
		}

		// Get respective guild member.
		var m *discordgo.Member
		if m, err = req.Sugo.Session.GuildMember(req.Channel.GuildID, req.Message.Author.ID); err != nil {
			return
		}

		// Build a list of member roles.
		var roles discordgo.Roles
		if roles, err = utils.RoleIDsToRoles(req, m.Roles); err != nil {
			return
		}

		// Try to filter role based on query.
		if roles, _, err = publicRoles.filter(req, roles, req.Query); err != nil {
			return
		}
		if len(roles) == 0 {
			resp = req.NewResponse(sugo.ResponseWarning, "", "you have no public roles with such name")
			return
		}
		if len(roles) > 1 {
			// TODO: better display what exactly roles were found
			resp = req.NewResponse(sugo.ResponseWarning, "", "you have multiple public with such name: ")
			return
		}
		var requestedRole *discordgo.Role
		requestedRole = roles[0]

		// Try to remove user role.
		err = req.Sugo.Session.GuildMemberRoleRemove(guild.ID, req.Message.Author.ID, requestedRole.ID)
		if err != nil {
			return nil, errors.Wrap(err, "unable to assign user role, make sure bot role is sorted above and bot has permission to manage roles")
		}

		// Respond about operation being successful.
		resp = req.NewResponse(
			sugo.ResponseSuccess,
			"",
			"you don't have `"+requestedRole.Name+"` role any more",
		)
		return
	},
}
