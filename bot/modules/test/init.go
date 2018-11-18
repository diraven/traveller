package test

import (
	"github.com/diraven/sugo"
)

// Init initializes module on the given bot.
func Init(sg *sugo.Instance) {
	sg.AddCommand(cmd)
}

var cmd = &sugo.Command{
	Trigger:     "test",
	Description: "command made for testing purposes\n",
	Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
		resp = req.SimpleResponse("test")
		return
	},
	SubCommands: []*sugo.Command{
		{
			Trigger: "subtest1",
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				resp = req.SimpleResponse("subtest1")
				return
			},
			SubCommands: []*sugo.Command{
				{
					Trigger: "subtest11",
					Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
						resp = req.SimpleResponse("subtest11")
						return
					},
				},
				{
					Trigger: "subtest12",
					Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
						resp = req.SimpleResponse("subtest12")
						return
					},
				},
			},
		},
		{
			Trigger: "subtest2",
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				resp = req.SimpleResponse("subtest2")
				return
			},
		},
		{
			Trigger: "plaintext",
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				_, err = req.NewResponse(
					sugo.ResponsePlainText,
					"message title",
					"message text",
				).Send()
				return
			},
		},
		{
			Trigger: "simple",
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				_, err = req.SimpleResponse("message text").Send()
				return
			},
		},
		{
			Trigger: "default",
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				_, err = req.NewResponse(
					sugo.ResponseDefault,
					"message title",
					"message text",
				).Send()
				return
			},
		},
		{
			Trigger: "info",
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				_, err = req.NewResponse(
					sugo.ResponseInfo,
					"message title",
					"message text",
				).Send()
				return
			},
		},
		{
			Trigger: "success",
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				_, err = req.NewResponse(
					sugo.ResponseSuccess,
					"message title",
					"message text",
				).Send()
				return
			},
		},
		{
			Trigger: "warning",
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				_, err = req.NewResponse(
					sugo.ResponseWarning,
					"message title",
					"message text",
				).Send()
				return
			},
		},
		{
			Trigger: "danger",
			Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
				_, err = req.NewResponse(
					sugo.ResponseDanger,
					"message title",
					"message text",
				).Send()
				return
			},
		},
	},
}
