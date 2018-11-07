package publicroles

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"gitlab.com/diraven/crabot/bot/utils"
	"sort"
	"strconv"
)

type sStat struct {
	role  *discordgo.Role
	count int
}

type tStats []sStat

func (ss *tStats) increment(role *discordgo.Role) {
	for i := range *ss {
		if (*ss)[i].role.ID == role.ID {
			(*ss)[i].count = (*ss)[i].count + 1
		}
	}
}

func (ss *tStats) Len() int {
	return len(*ss)
}
func (ss *tStats) Less(i, j int) bool {
	return (*ss)[i].count < (*ss)[j].count
}

func (ss *tStats) Swap(i, j int) {
	(*ss)[i], (*ss)[j] = (*ss)[j], (*ss)[i]
}

var statsCmd = &sugo.Command{
	Trigger:     "stats",
	Description: "Lists public roles with the highest/lowest count of people.",
	HasParams:   true,
	Execute: func(req *sugo.Request) (err error) {
		// Get guild.
		var guild *discordgo.Guild
		if guild, err = req.GetGuild(); err != nil {
			return
		}

		// Get all public roles.
		var roles discordgo.Roles
		if roles, _, err = publicRoles.filter(req, guild.Roles, ""); err != nil {
			return
		}

		// Make a storage for stats we are about to gather.
		stats := &tStats{}

		// Fill stats with zero values.
		for _, role := range roles {
			*stats = append(*stats, sStat{
				role,
				0,
			})
		}

		// Make members array we will be working with.
		for _, member := range guild.Members {
			for _, roleID := range member.Roles {
				for _, role := range roles {
					// Check if user has role
					if role.ID == roleID {
						stats.increment(role)
					}
				}
			}
		}

		// Sort people.
		sort.Sort(stats)

		// Reverse results if we want bottom side of the chart
		if req.Query != "bottom" {
			sort.Sort(sort.Reverse(stats))
		}

		if len(*stats) > 0 {
			// Start building response.
			var response string
			for i, stat := range *stats {
				response = response + strconv.Itoa(i+1) + ". " + utils.RoleToMention(stat.role) + " (" + strconv.Itoa(stat.count) + ")\n"
				if i > 9 {
					break
				}
			}
			response = response + ""
			if _, err = req.NewResponse(sugo.ResponseInfo, "", response).Send(); err != nil {
				return
			}
		} else {
			if _, err = req.NewResponse(sugo.ResponseWarning, "", "no data available").Send(); err != nil {
				return
			}
		}

		return
	},
}
