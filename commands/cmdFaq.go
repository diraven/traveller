package commands

import (
	"log"

	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/state"
)

type faqEntry struct {
	title string
	text  string
}

var faqEntries = map[string]*discordgo.MessageEmbed{
	"ru-interface": {
		Title: "Російськомовний інтерфейс",
		Description: `Розгляньте, будь ласка, можливість змінити мову інтерфейсу на українську або англійську.

Розробники ПО та ігор послуговуються статистикою щодо використання мов інтерфейсу і приймають рішення в тому числі базуючись на ній щодо локалізації ігор та доступності мов. В тому числі і українські студії.

Наприклад, таку статистику [пропонує Steam](https://store.steampowered.com/hwsurvey/Steam-Hardware-Software-Survey-Welcome-to-Steam) (секція "Language").

Регіональний поділ аудиторії відбувається в тому числі за мовою: доходило до того, що деякі ігри Ubisoft та EA певний час були недоступні англійською для України. А в Lost Ark та деяких інших ММО нас взагалі насильно загнали в ру регіон без права вибору.

Купа ігор доступні українською завдяки нашим перекладачам-волонтерам, які на то витрачають купу власного часу. Kingdom Come: Deliverance, Satisfactory, Deep Rock Galactic, Factorio. Такі ініціативи варто підтримувати. І найкраща підтримка - грати українською. Зіграйте, не пошкодуєте!

Зі зростанням кількості користувачів україномовного інтерфейсу зростатимуть, відповідно, кількість і якість локалізацій. Й тим швидше вони з'являтимуться. Можливо, з часом, навіть на релізі!

Споживаймо відповідально. Дякую!`,
	},
	"apolitical": {
		Title: "Поза політикою",
		Description: `Політика - це діяльність, спрямована на управління державою. Законодавство - це політика. Закони визначають правила нашого з вами життя та взаємодії в суспільстві. А тому політика - це все. Медицина, освіта, ціна ковбаси в магазині чи роздовбана дорога - це політика. Ваше авто, чай на сніданок і хліб з маслом - це політика. Ваш (не)спокійний сон та вибухи за вікном - теж політика. Спорт в будь-яких його проявах - теж політика, як частина суспільного життя. Від політики нікуди не дітися і не сховатися, вона всюди.

Тому сентенції на кшталт "ігри поза політикою" чи "спорт поза політикою" щонайменше неправдиві. Щонайбільше - небезпечні. Люди, що позиціонують себе "поза політикою", свідомо відмовляються від відповідальності за власне життя і майбутнє, віддаючи його в руки тих, хто "в політиці". Вибір за вас зробить інший, а з наслідками цього вибору доведеться жити вам.

Тому політика - це важливо. Брати в ній участь і впливати на суспільні процеси - теж важливо. Писати листи, запити, вимагати дотримання своїх прав і свобод. Джерелом влади в Україні є народ. Суспільний запит визначає курс держави. І починається з окремих людей та простих дій.`,
	},
	"svc": {
		Title: "СВЦ, Синдром Великого Цабе",
		Description: `Морально-психологічний стан, що характеризується надмірним почуттям власної важливості.
        
**Групи ризику:** лідери думок, публічні люди, люди що мають певну владу.
**Ускладнення:**  гостра форма має тенденцію до переходу в хронічну з плином часу, що, в свою чергу, може призвести до егоцентризму та нарцисизму. Наявний егоцентризм та/або нарцисизм ускладнює перебіг синдрому та прискорює перехід синдрому в хронічну форму.
**Лікування:** зняти корону. Можливе симптоматичне лікування фейспалмами. У випадку рецидивів: призначити підтримуючу терапію - суспільно корисні роботи.
		`,
	},
	"spoiler_mobile": {
		Title: "Спойлер на тілібоні",
		Description: `1. Після того як ви обрали фото, тицьніть кніпку назад на тілібоні, щоб закрити вікно з галереєю (рис. 1).
2. Тицьніть на обране фото на вікні вкладень ще раз (рис. 2).
3. Тицьніть на позначку "позначити як спойлер" (рис. 3).
		
Вуаля, спойлер на тілібоні. Не так вже й складно, е?
		`,
		Image: &discordgo.MessageEmbedImage{URL: "https://cdn.discordapp.com/attachments/997173042662887514/997174604856565841/spoiler.png"},
	},
	"language": {
		Title: "Мова спілкування?",
		Description: `Мови спілкування на сервері - українська та англійська. Перегляньте, будь ласка, це та інші правила в відповідному каналі.

Server languages: Ukrainian and English. Please, see this and other rules in the respective channel.
		`,
	},
	"russians": {
		Title:       "Чому росіян варто називати росіянами?",
		Description: `Навішуючи ярлики типу "орки" чи "свинособаки" ми свідомо дистанціюємо ті звірства що вони роблять від них самих. Відокремлюємо росіян від їх злочинів, приписуючи це міфічним "оркам". В своїй свідомости та в свідомості суспільств за кордоном. Це як підміняти війну словосполученням "Спеціяльна Військова Операція". Не варто. Воюють проти нас, насилують та вбивають реальні люди, громадяни росії, себто росіяни. Так, це звучить некомфортно в порівнянні з "орками", але тут краще дивитися правді у вічі і називати речі своїми іменами.`,
	},
	"russian_spoiler": {
		Title:       "Чому весь російськомовний контент варто заганяти під спойлер?",
		Description: `Мова - це, в тому числі, зброя. Зброя потужна. Така, що нищить в тилу без всяких ракет та артилерії. Російську мову використовують проти нас відповідно. Там де є російська, себто в російськомовному інфопросторі - шанс натрапити на наративи вигідні РФ значно вищий. Чим більше ми послуговуємося російською - говоримо, читаємо, дивимось, ділимось - тим вразливіші ми для цієї зброї, як нація. Сьогодні смішний відосик російською, завтра стаття, післязавтра аналітика, а за кілька років - російські новини. Повзуча культурна окупація відбувається не перше десятиліття. Озирніться навколо. Навіщо спрощувати ворогу його задачу?`,
	},
}

var cmdFaq = &Command{

	Init: func(s *discordgo.Session, state *state.State) error {
		// Register command.
		options := make([]*discordgo.ApplicationCommandOption, len(faqEntries))
		i := 0
		for name, entry := range faqEntries {
			options[i] = &discordgo.ApplicationCommandOption{
				Name:        name,
				Description: entry.Title,
				Type:        discordgo.ApplicationCommandOptionSubCommand,
			}
			i++

		}

		definition := &discordgo.ApplicationCommand{
			Name:        "faq",
			Description: "ЧаПи",
			Options:     options,
		}
		for GuildID := range state.Guilds {
			_, err := s.ApplicationCommandCreate(s.State.User.ID, GuildID, definition)
			if err != nil {
				log.Panicf("Cannot create '%v' command: %v", definition.Name, err)
			}
		}

		// Add handler.
		s.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
			if i.ApplicationCommandData().Name != definition.Name {
				return
			}

			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Embeds: []*discordgo.MessageEmbed{
						faqEntries[i.ApplicationCommandData().Options[0].Name],
					},
				},
			})
		})

		return nil
	},
}
