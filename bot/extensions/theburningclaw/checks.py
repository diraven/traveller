from core.context import Context
from extensions.theburningclaw.models import Character


async def has_character(ctx: Context):
    """Check if user is registered via discord social auth."""
    # noinspection PyUnresolvedReferences
    ctx.character = await Character.get_or_create(
        user_id=ctx.socialaccount.user_id,
        character_name=ctx.author.display_name,
    )
    return True
