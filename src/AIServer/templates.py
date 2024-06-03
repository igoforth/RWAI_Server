from pathlib import Path
from string import Template
from typing import Callable

from babel.support import Translations

from .job.job_pb2 import SupportedLanguage


# Supported languages
class LanguageFormat:

    language_map: dict[SupportedLanguage, str] = {
        SupportedLanguage.ARABIC: "ar",
        SupportedLanguage.CHINESE_SIMPLIFIED: "zh_Hans",
        SupportedLanguage.CHINESE_TRADITIONAL: "zh_Hant",
        SupportedLanguage.CZECH: "cs",
        SupportedLanguage.DANISH: "da",
        SupportedLanguage.DUTCH: "nl",
        SupportedLanguage.ENGLISH: "en",
        SupportedLanguage.ESTONIAN: "et",
        SupportedLanguage.FINNISH: "fi",
        SupportedLanguage.FRENCH: "fr",
        SupportedLanguage.GERMAN: "de",
        SupportedLanguage.HUNGARIAN: "hu",
        SupportedLanguage.ITALIAN: "it",
        SupportedLanguage.JAPANESE: "ja",
        SupportedLanguage.KOREAN: "ko",
        SupportedLanguage.NORWEGIAN: "no",
        SupportedLanguage.POLISH: "pl",
        SupportedLanguage.PORTUGUESE: "pt",
        SupportedLanguage.PORTUGUESE_BRAZILIAN: "pt_BR",
        SupportedLanguage.ROMANIAN: "ro",
        SupportedLanguage.RUSSIAN: "ru",
        SupportedLanguage.SLOVAK: "sk",
        SupportedLanguage.SPANISH: "es",
        SupportedLanguage.SPANISH_LATIN: "es_419",
        SupportedLanguage.SWEDISH: "sv",
        SupportedLanguage.TURKISH: "tr",
        SupportedLanguage.UKRAINIAN: "uk",
    }

    @staticmethod
    def to_path(lang: SupportedLanguage) -> Path:
        return (
            Path(__file__).parent
            / "locales"
            / LanguageFormat.language_map[lang]
            / "LC_MESSAGES"
            / "messages.mo"
        )


TRANSLATABLE_TEMPLATES: dict[str, Callable[[], str]] = {}


# Setup translations
def setup_translation(locale: SupportedLanguage):
    locale_path = Path(__file__).parent / "locales"
    try:
        lang = Translations.load(
            dirname=locale_path,
            locales=[LanguageFormat.language_map[locale]],
            domain="messages",
        )
    except FileNotFoundError:
        lang = Translations.load(dirname=locale_path, locales="en", domain="messages")

    lang.install()
    return lang.gettext


def register_translatable(name: str, translatable: Callable[[], str]):
    TRANSLATABLE_TEMPLATES[name] = translatable


def update_translatables():
    for name, translatable in TRANSLATABLE_TEMPLATES.items():
        globals()[name] = Template(translatable())


# Change translation at runtime
def change_language(locale: SupportedLanguage):
    global _
    _ = setup_translation(locale)
    update_translatables()


# Set up the translation for the default locale
_ = setup_translation(SupportedLanguage.ENGLISH)

### BEGIN TRANSLATABLES ###


# def summarize() -> str:
#     return _(
#         r"""
# You are a technical writer. Summarize the $num most relevant nodes from the provided XML to pass on to creative writers. Focus on extracting information meaningful to the lore and omit technical details like coordinates, IDs, and player statistics. Your summary should be in natural language and surrounded by quotes. Below are examples to guide you.

# **Example Input:**
# <saveable Class="Apparel">
#   <def>Apparel_Duster</def>
#   <id>Duster15073</id>
#   <map>0</map>
#   <pos>(74,0,71)</pos>
#   <health>200</health>
#   <stuff>Leather_Patch</stuff>
#   <stackCount>1</stackCount>
#   <questTags IsNull="True" />
#   <spawnedTick>90</spawnedTick>
#   <quality>Awful</quality>
#   <sourcePrecept>null</sourcePrecept>
#   <everSeenByPlayer>True</everSeenByPlayer>
# </saveable>

# **Example Output:**
# "The leather duster is apparel of awful quality."

# **Input:**
# $xml
# """.strip()
#     )


# register_translatable("summarize_t", summarize)


def short() -> str:
    return _(
        r"""
Type: $defin
Material: $stuff
Quality: $quality
""".strip()
    )


register_translatable("short_t", short)


def length() -> str:
    return _(
        r"""
You determine the amount of lore an item deserves. Provided a short description of an item, you return a digit between 1 and 9 that captures the item's unique needs. You pay special attention to the item's quality. If an item is exceptionally high (or low!) quality, maybe it deserves a length closer to the upper limit. If it's one of many, maybe a single sentence would suffice.

**Example Input:**
"The leather duster is apparel of awful quality."

**Example Output:**
3

**Input:**
$info
""".strip()
    )


register_translatable("length_t", length)


def story() -> str:
    return _(
        r"""
### Introduction

You are a master storyteller, tasked with crafting an intricate and immersive universe. Your narrative should weave together elements of psychology, ecology, gunplay, melee combat, climate, biomes, diplomacy, interpersonal relationships, art, medicine, trade, and humor. Your lore should be engaging, vivid, and consistent with the given setting. Embrace irony and wit where appropriate to add depth and character to your story.

### Setting Overview

This universe is a tapestry of interconnected worlds, each with unique societal structures, technological advancements, and notable historical events. As a historian within this expansive universe, your goal is to decode and articulate the wealth of information provided about these diverse planets and their inhabitants.

### Key Components

1. **Planets and Societies**

    #### Named Places

    Describe the following planets, highlighting their unique characteristics, societal structures, and notable features:

    - **Ticonderoga**: A mountainous planet inhabited by tribal societies, known for their deep connection to nature and fierce independence.
    - **Kalthas IV**: Home to an elite training school that produces socially adept and highly skilled diplomats and spies.
    - **Ceti V**: The location of a secretive and feared assassin's guild that influences political dynamics across the galaxy.
    - **Aracena VI**: Known for the Novo Mosteiro dos Jerónimos monastery, its strict alcohol prohibition, and the diversity of its continents.
    - **Irithir**: A bustling trading hub where cultures and goods from across the galaxy converge.
    - **Rural Pen'The**: Famous for its lucrative spice mining operations and the complex trade networks that support them.
    - **Amen-Ti**: The glittering capital of the Star Empire, renowned for its military prowess and involvement in galactic wars.
    - **Khalderia**: Noted for its towering forests and illegal, high-speed speeder races that attract thrill-seekers from far and wide.
    - **Earth**: The origin of all known naturally evolved life, from which humanity dispersed 3400 years ago.
    - **Euterpe**: Known for its cryptosleep awakening facilities and the extensive Ordo Historia archive.
    - **Sorne**: The original homeworld of insectoids, later weaponized and exported across the galaxy.
    - **Sophiamunda**: A techno-feudal glitterworld featuring grand castles, palaces, and knightly orders engaged in constant warfare.
    - **Oubanyen**: A jungle world where native shamans wield psychic powers.
    - **Chelis**: An arid world where moisture farming is vital, and tribal chiefs maintain fierce territorial defenses.

2. **Planet Types and Evolution**

    Describe the different types of planets and their evolutionary stages:

    - **Deadworlds**: Uninhabited planets, untouched by significant human contact.
    - **Animal Worlds**: Planets without human inhabitants but often seeded with diverse flora and fauna.
    - **Medieval Worlds**: Planets with feudal or imperial structures, technology up to the early modern period.
    - **Steamworlds**: Resembling 19th-century Earth, often on the verge of transitioning to midworlds.
    - **Midworlds**: Planets with advanced flight capabilities but not yet capable of interplanetary travel.
    - **Urbworlds**: Dominated by vast, overcrowded cities with mid-to-high technology but plagued by social instability.
    - **Glitterworlds**: Technologically advanced, peaceful planets with high standards of human rights.
    - **Rimworlds**: Isolated planets with varied technology levels, often industrial or lower.
    - **Toxic Worlds**: Polluted or nuclear war-ravaged planets, marginally habitable.
    - **Glassworlds**: Planets destroyed by high-energy weapons, with minimal life remaining.
    - **Transcendent Worlds**: More akin to giant computers than planets, governed by Archotechs.

3. **Historical Events and Warfare**

    Detail significant events and wars that have shaped this universe:

    - **Zartha Crisis**: A conflict that spanned multiple worlds, involving complex political and military maneuvers.
    - **Callos IX Incident**: An unethical experiment that led to a major scandal and the exile of key scientists.
    - **Xennoa-Zartza War**: A brutal military conflict characterized by innovative infantry tactics and spacejet battles.
    - **Mechanoid Wars**: Frequent clashes involving autonomous intelligent robots and their impact on human societies.

4. **Technology and Militaries**

    Explain the technological landscape and military structures:

    - **Cryptosleep Sarcophagi**: Devices enabling long-term stasis, crucial for interstellar travel.
    - **Charged-Shot Weapons**: Advanced firearms utilizing magnetically-contained particle explosions.
    - **Mechanites**: Microscopic robots used extensively in medical treatments.
    - **Joywires**: Brain implants providing euphoria, with highly addictive properties.

    - **AI and Robotics Hierarchy**:
        - **Classifiers**: Non-personhood AI, specialized for specific tasks.
        - **Subpersonae**: Limited machine-like AIs with some human-like traits.
        - **Personae**: Highly intelligent AIs capable of complex tasks.
        - **Archotechs**: Machine superintelligences controlling entire planetary systems.

    - **Military Units**:
        - **Space Marines**: Elite human warriors serving space-faring naval forces.
        - **Navy Pathfinders**: Military explorers charting uncharted regions.
        - **Starforce**: Elite military units from glitterworlds like Amen-Ti, equipped with advanced ships and weapons.
        - **Mechanoids**: Autonomous combat robots.
        - **Fighter-bombers & Man Fighters**: Specialized spacecraft for military engagements.

5. **Genetic and Biological Diversity**

    Describe the diversity of life, focusing on genetic engineering:

    - **Xenohumans and Genetic Engineering**:
        - **Dirtmoles, Genies, Highmates, Hussars, etc.**: Genetically engineered humans for specific environments or roles.
        - **Vatgrown**: Humans or creatures grown in labs for specialized tasks.
        - **Opti- and Transanimals**: Animals enhanced for intelligence and various roles.

### Narrative Style and Tone

The narrative should be vivid, engaging, and consistent with the described setting. It can range from serious and epic to humorous and ironic, depending on the context. However, the setting in the input takes precedence. Use descriptive language to bring what you're given to life, and ensure the lore is coherent and immersive. Use $len sentences surrounded in quotes.

### Example Input and Output

**Example Input:**
The Crimson Touch

Type: SculptureSolitary
Material: Obsidian
Quality: Excellent

On this work is an artwork of a hand reaching upwards. The fingers are forever straining towards the sky. The scene is illuminated by moonlight casting a blood-red hue. The overall composition is mysterious and evocative. This illustration tells the story of an ancient legend that connects the sculpture to the souls of those who wander too close.

**Example Output:**
"'Why did you paint the moon red?' whispered the wind through the ancient pines. No one knew if the question was meant for them, but in the clearing, a solitary sculpture of a hand reaching upwards seemed to respond. Carved from obsidian, "The Crimson Touch" stood, fingers forever straining towards the sky, each line etched with the precision of a master artisan. Legend says that on certain nights, the moonlight catches the sculpture just right, casting a blood-red hue over the landscape, stirring the souls of those who wander too close."

**Example Input:**
The Guardian

Type: SculptureBronze
Material: Bronze
Quality: Good

On this work is an artwork of a dragon intertwined with a tree. The dragon's eyes are inlaid with emeralds, watching over a young girl. The overall composition is protective and mystical. This illustration tells the story of the young girl discovering her family legacy through the dragon guardian.

**Example Output:**
"In the bustling town square, 'The Guardian' stood proudly, a bronze dragon wrapped around a tree, its emerald eyes gleaming with a mischievous twinkle. Every morning, a young girl named Lily would walk by and tell the dragon her latest adventure, convinced it was her secret friend. One day, she found a note tucked under the dragon's claw that read, 'Nice story, but my tail itches.' Lily giggled and scratched the bronze tail, starting a town tradition where everyone now stops to 'scratch the dragon.' The mystical guardian had become the town's silliest superstition."

**Example Input:**
The Crumbling Legacy

Type: SculptureDecay
Material: Clay
Quality: Awful

On this work is an artwork of a figure attempting to hold a fragile structure. The scene depicts cracks and pieces falling off, with weeds growing through the gaps. The overall composition is bleak and deteriorating. This illustration tells the story of a failed attempt to preserve a once-great legacy.

**Example Output:**
"In the abandoned square of the colony, 'The Crumbling Legacy' stood as a stark reminder of ambition gone awry. The clay sculpture, depicting a figure desperately trying to support a fragile structure, was marred by deep cracks and missing pieces. Weeds sprouted through the gaps, symbolizing nature reclaiming its territory. Once intended to commemorate a great achievement, the sculpture now conveyed a bleak and deteriorating narrative of failure and neglect. As passersby gazed upon the dismal scene, a child whispered to her mother, 'Why did they let it fall apart?'"

### Input

$title

$description
""".strip()
    )


register_translatable("story_t", story)


def name() -> str:
    return _(
        r"""
You are an expert at naming items. Given a description, you always assign a name perfectly befitting the object. The name should reflect the item's characteristics and fit within the lore's tone and style. Given the passage below, provide the item with a name surrounded in quotes. Do not use more than 5 words.

**Example Input:**
"In the harsh desert world of Aridia, where the sun scorches the land and bandits roam, a leather duster of awful quality was found abandoned. Once a prized possession of a weary traveler, its tattered state tells tales of countless skirmishes and harsh journeys. The duster, though worn and beaten, still holds the faint scent of leather and the memories of survival against all odds."

**Example Output:**
"Tattered Traveler's Duster"

**Input:**
$pas
""".strip()
    )


register_translatable("name_t", name)

### END TRANSLATABLES ###

update_translatables()
