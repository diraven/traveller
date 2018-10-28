package publicroles

import (
	"github.com/diraven/sugo"
)

// Init initializes module on the given bot.
func Init(sg *sugo.Instance) (err error) {
	return sg.AddCommand(cmd)
}
