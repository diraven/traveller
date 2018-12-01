package publicroles

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"github.com/pkg/errors"
)

var joinCmd = &sugo.Command{
	Trigger:     "join",
	Description: "Joins person to the public role.",
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

		// Try to filter role based on query.
		var roles discordgo.Roles
		if roles, _, err = publicRoles.filter(req, guild.Roles, req.Query); err != nil {
			return
		}
		if len(roles) == 0 {
			resp = req.NewResponse(sugo.ResponseWarning, "", "no public roles found with such name")
			return
		}
		if len(roles) > 1 {
			// TODO: better display what exactly roles were found
			resp = req.NewResponse(sugo.ResponseWarning, "", "multiple public roles found: ")
			return
		}
		var requestedRole *discordgo.Role
		requestedRole = roles[0]

		// Get respective guild member.
		var m *discordgo.Member
		if m, err = req.Sugo.Session.GuildMember(req.Channel.GuildID, req.Message.Author.ID); err != nil {
			return
		}

		// For each member's public role:
		for _, roleID := range m.Roles {
			if roleID == requestedRole.ID {
				resp = req.NewResponse(sugo.ResponseWarning, "", "you already have this role")
				return
			}
		}

		// Try to assign user a role.
		if err = req.Sugo.Session.GuildMemberRoleAdd(guild.ID, req.Message.Author.ID, requestedRole.ID); err != nil {
			return nil, errors.Wrap(err, "unable to assign user role, make sure bot role is sorted above and bot has permission to manage roles")
		}

		// Response regarding successful operation.
		resp = req.NewResponse(sugo.ResponseSuccess, "", "you have got a `"+requestedRole.Name+"` role")
		return
	},
}
