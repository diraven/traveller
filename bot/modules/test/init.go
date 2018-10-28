package test

import (
	"github.com/diraven/sugo"
)

// Init initializes module on the given bot.
func Init(sg *sugo.Instance) (err error) {
	return sg.AddCommand(cmd)
}

var cmd = &sugo.Command{
	Trigger:     "test",
	Description: "command made for testing purposes\n asdf fdsa",
	Execute: func(req *sugo.Request) (err error) {
		_, err = req.RespondInfo("", "test passed")
		return
	},
	SubCommands: []*sugo.Command{
		{
			Trigger: "subtest1",
			Execute: func(req *sugo.Request) (err error) {
				_, err = req.RespondInfo("", "subtest1 passed")
				return
			},
			SubCommands: []*sugo.Command{
				{
					Trigger: "subtest11",
					Execute: func(req *sugo.Request) (err error) {
						_, err = req.RespondInfo("", "subtest11 passed")
						return
					},
				},
				{
					Trigger: "subtest12",
					Execute: func(req *sugo.Request) (err error) {
						_, err = req.RespondInfo("", "subtest12 passed")
						return
					},
				},
			},
		},
		{
			Trigger: "subtest2",
			Execute: func(req *sugo.Request) (err error) {
				_, err = req.RespondInfo("", "subtest2 passed")
				return
			},
		},
		{
			Trigger: "responses",
			Execute: func(req *sugo.Request) (err error) {
				if _, err = req.Respond("", "default", sugo.ColorPrimary, ""); err != nil {
					return
				}
				if _, err = req.RespondInfo("", "info"); err != nil {
					return
				}
				if _, err = req.RespondSuccess("", "success"); err != nil {
					return
				}
				if _, err = req.RespondWarning("", "warning"); err != nil {
					return
				}
				if _, err = req.RespondDanger("", "failure"); err != nil {
					return
				}
				return
			},
		},
	},
}
