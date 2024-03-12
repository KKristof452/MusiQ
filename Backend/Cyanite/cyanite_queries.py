import hashlib
import hmac
import logging


class CyaniteQueries():
    file_upload_request = """
        mutation FileUploadRequestMutation {
            fileUploadRequest {
                # the id will be used for creating the library track from the file upload
                id
                # the uploadUrl specifies where we need to upload the file to
                uploadUrl
            }
        }
    """

    library_track_creation = """
        mutation LibraryTrackCreateMutation($input: LibraryTrackCreateInput!) {
            libraryTrackCreate(input: $input) {
                __typename
                ... on LibraryTrackCreateSuccess {
                    createdLibraryTrack {
                        id
                    }
                }
                ... on LibraryTrackCreateError {
                    code
                    message
                }
            }
        }
    """

    library_track_query = """
        query LibraryTrackQuery($libraryTrackId: ID!) {
            libraryTrack(id: $libraryTrackId) {
                __typename
                ... on LibraryTrackNotFoundError {
                    message
                }
                ... on LibraryTrack {
                    id
                    title
                    audioAnalysisV6 {
                        __typename
                        ... on AudioAnalysisV6Finished {
                            result {
                                voicePresenceProfile
                                predominantVoiceGender
                                voice {
                                    female
                                    male
                                    instrumental
                                }
                                voiceTags
                                mood {
                                    aggressive
                                    calm
                                    chilled
                                    dark
                                    energetic
                                    epic
                                    happy
                                    romantic
                                    sad
                                    scary
                                    sexy
                                    ethereal
                                    uplifting
                                }
                                moodTags
                                moodMaxTimes {
                                    mood
                                    start
                                    end
                                }
                                moodAdvanced {
                                    anxious
                                    barren
                                    cold
                                    creepy
                                    dark
                                    disturbing
                                    eerie
                                    evil
                                    fearful
                                    mysterious
                                    nervous
                                    restless
                                    spooky
                                    strange
                                    supernatural
                                    suspenseful
                                    tense
                                    weird
                                    aggressive
                                    agitated
                                    angry
                                    dangerous
                                    fiery
                                    intense
                                    passionate
                                    ponderous
                                    violent
                                    comedic
                                    eccentric
                                    funny
                                    mischievous
                                    quirky
                                    whimsical
                                    boisterous
                                    boingy
                                    bright
                                    celebratory
                                    cheerful
                                    excited
                                    feelGood
                                    fun
                                    happy
                                    joyous
                                    lighthearted
                                    perky
                                    playful
                                    rollicking
                                    upbeat
                                    calm
                                    contented
                                    dreamy
                                    introspective
                                    laidBack
                                    leisurely
                                    lyrical
                                    peaceful
                                    quiet
                                    relaxed
                                    serene
                                    soothing
                                    spiritual
                                    tranquil
                                    bittersweet
                                    blue
                                    depressing
                                    gloomy
                                    heavy
                                    lonely
                                    melancholic
                                    mournful
                                    poignant
                                    sad
                                    frightening
                                    horror
                                    menacing
                                    nightmarish
                                    ominous
                                    panicStricken
                                    scary
                                    concerned
                                    determined
                                    dignified
                                    emotional
                                    noble
                                    serious
                                    solemn
                                    thoughtful
                                    cool
                                    seductive
                                    sexy
                                    adventurous
                                    confident
                                    courageous
                                    resolute
                                    energetic
                                    epic
                                    exciting
                                    exhilarating
                                    heroic
                                    majestic
                                    powerful
                                    prestigious
                                    relentless
                                    strong
                                    triumphant
                                    victorious
                                    delicate
                                    graceful
                                    hopeful
                                    innocent
                                    intimate
                                    kind
                                    light
                                    loving
                                    nostalgic
                                    reflective
                                    romantic
                                    sentimental
                                    soft
                                    sweet
                                    tender
                                    warm
                                    anthemic
                                    aweInspiring
                                    euphoric
                                    inspirational
                                    motivational
                                    optimistic
                                    positive
                                    proud
                                    soaring
                                    uplifting
                                }
                                moodAdvancedTags
                                genre {
                                    ambient
                                    blues
                                    classical
                                    electronicDance
                                    folkCountry
                                    funkSoul
                                    jazz
                                    latin
                                    metal
                                    pop
                                    rapHipHop
                                    reggae
                                    rnb
                                    rock
                                    singerSongwriter
                                }
                                genreTags
                                advancedGenre {
                                    afro
                                    ambient
                                    arab
                                    asian
                                    blues
                                    childrenJingle
                                    classical
                                    electronicDance
                                    folkCountry
                                    funkSoul
                                    indian
                                    jazz
                                    latin
                                    metal
                                    pop
                                    rapHipHop
                                    reggae
                                    rnb
                                    rock
                                    singerSongwriters
                                    sound
                                    soundtrack
                                    spokenWord
                                }
                                advancedGenreTags
                                bpmPrediction {
                                    value
                                    confidence
                                }
                                bpmRangeAdjusted
                                keyPrediction {
                                    value
                                    confidence
                                }
                            }
                        }
                    }
                }
            }
        }
    """
