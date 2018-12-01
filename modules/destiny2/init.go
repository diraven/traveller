package destiny2

import (
	"github.com/diraven/sugo"
	"strings"
)

// Init initializes module on the given bot.
func Init(sg *sugo.Instance) {
	sg.AddCommand(cmd)
}

var cmd = &sugo.Command{
	Trigger:     "destiny2",
	Description: "Destiny 2 related commands",
	SubCommands: []*sugo.Command{
		{
			Trigger:   "map",
			HasParams: true,
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				resp = req.PlainTextResponse("https://lowlidev.com.au/destiny/maps/")

				if req.Query != "" {
					var knownLocations = map[string]interface{}{
						"tower":         nil,
						"farm":          nil,
						"earth":         nil,
						"titan":         nil,
						"nessus":        nil,
						"mars":          nil,
						"io":            nil,
						"tangled-shore": nil,
						"dreaming-city": nil,
					}

					var found string

					for location := range knownLocations {
						if strings.Contains(location, req.Query) {
							found = location
							break
						}
					}

					if found != "" {
						resp = req.PlainTextResponse("https://lowlidev.com.au/destiny/maps/" + found)
					} else {
						resp = req.NewResponse(sugo.ResponseWarning, "", "map with such name was not found")
					}
				}

				return
			},
		},
		{
			Trigger: "xur",
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				resp = req.SimpleResponse("https://whereisxur.com/")
				return
			},
		},
	},
}
