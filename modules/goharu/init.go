package goharu

import (
	"github.com/diraven/sugo"
	"io/ioutil"
	"net/http"
	"regexp"
)

// Init initializes module on the given bot.
func Init(sg *sugo.Instance) {
	sg.AddCommand(cmd)
}

// TODO: Make a better caching mechanism.
var cachedText string

var cmd = &sugo.Command{
	Trigger:     "goharu",
	Description: "GoHa.ru forums search.",
	HasParams:   true,
	Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
		resp = req.PlainTextResponse("https://www.goha.ru/")

		// If query is provided.
		if req.Query != "" {
			// Make sure query is long enough.
			if len(req.Query) < 3 {
				resp = req.NewResponse(sugo.ResponseDanger, "", "query must contain at least 3 symbols")
				return
			}

			// If cached data is not available:
			if cachedText == "" {
				// Load goha archive page.
				var response *http.Response
				response, err = http.Get("https://forums.goha.ru/archive/index.php")
				if err != nil {
					resp = req.NewResponse(sugo.ResponseDanger, "", err.Error())
					return
				}
				defer response.Body.Close()

				// Make sure response is provided and status is 200-ok.
				if response.StatusCode != http.StatusOK {
					resp = req.NewResponse(sugo.ResponseDanger, "", response.Status)
					return
				}

				var data []byte
				data, err = ioutil.ReadAll(response.Body)
				if err != nil {
					resp = req.NewResponse(sugo.ResponseDanger, "", "internal error, contact developer for details")
					return
				}

				cachedText = string(data)
			}

			// Try to find relevant url.
			var rexp *regexp.Regexp
			rexp, err = regexp.Compile(`(?i)<a href="[^"]*f-(\d+)[^"]+">.*` + regexp.QuoteMeta(req.Query) + `[^<]*</a>`)
			var results [][]string
			results = rexp.FindAllStringSubmatch(cachedText, -1)

			// If there are no results:
			if len(results) == 0 {
				resp = req.SimpleResponse("nothing found")
				return
			}

			// Show results to the user.
			var url = "https://forums.goha.ru/forumdisplay.php?f=" + results[0][1]
			resp = req.PlainTextResponse(url)

			return
		}

		return
	},
}
