use poise::serenity_prelude::CreateEmbed;
use poise::serenity_prelude::Embed;

use crate::{Context, Error};

/// Show this help menu
#[poise::command(slash_command)]
pub async fn faq(
    ctx: Context<'_>,
    #[description = "Specific command to show help about123"]
    #[autocomplete = "poise::builtins::autocomplete_command"]
    command: Option<String>,
) -> Result<(), Error> {
    // Post a text embed.
    // let mut embed = CreateEmbed::default();
    // embed.title("test title");
    // embed.description("test description");
    // embed.color(0x00ff00);
    // let embed: Embed = embed.into();

    // ctx.reply(ctx.data(), |e| e.embed(embed)).await?;
    ctx.say("tes122t").await?;

    Ok(())
}
