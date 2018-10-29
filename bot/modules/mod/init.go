package mod

import (
	"github.com/diraven/sugo"
)

// Init initializes module on the given bot.
func Init(sg *sugo.Instance) (err error) {
	return sg.AddCommand(cmd)
}

// Info shows some general bot info.
var cmd = &sugo.Command{
	Trigger:     "mod",
	Description: "A set of moderation commands.",
	SubCommands: []*sugo.Command{
		clear,
	},
}
