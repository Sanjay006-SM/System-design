import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.topic import Topic, UserTopic
from backend.app.models.article import Article, ArticleTopic
from backend.app.models.interaction import Interaction
from backend.app.models.notification import Notification

logger = logging.getLogger("db.seed")

DEMO_TOPICS = [
    {"name": "Artificial Intelligence", "slug": "artificial-intelligence"},
    {"name": "Technology", "slug": "technology"},
    {"name": "Space & Science", "slug": "space-science"},
    {"name": "Business & Economy", "slug": "business-economy"},
    {"name": "Global Politics", "slug": "global-politics"},
    {"name": "Cybersecurity", "slug": "cybersecurity"},
    {"name": "Clean Energy & Climate", "slug": "clean-energy-climate"},
    {"name": "Sports & Athletics", "slug": "sports-athletics"},
    {"name": "Health & Biotech", "slug": "health-biotech"},
    {"name": "Automotive & EV", "slug": "automotive-ev"}
]

DEMO_USERS = [
    {"id": 101, "username": "alex_chen", "email": "alex.chen@example.com"},
    {"id": 102, "username": "priya_sharma", "email": "priya.sharma@example.com"},
    {"id": 103, "username": "david_miller", "email": "david.miller@example.com"},
    {"id": 104, "username": "elena_rostova", "email": "elena.rostova@example.com"}
]

DEMO_ARTICLES = [
    {
        "title": "Open-Source Foundation Models Rival Proprietary Frontier Architectures",
        "description": "Researchers reveal benchmark results showing open-weight transformer models achieving near-parity in complex multi-step reasoning benchmarks.",
        "content": "A milestone breakthrough in distributed machine learning was unveiled today as open-weights models demonstrated competitive scores across MMLU, GSM8K, and HumanEval benchmarks. Industry analysts anticipate this will accelerate on-premise AI deployments for enterprise security.",
        "source": "TechCrunch (Demo)",
        "author": "Marcus Sterling",
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["artificial-intelligence", "technology"],
        "view_count": 1420,
        "engagement_count": 310,
        "hours_ago": 2
    },
    {
        "title": "Next-Gen Quantum Computing Chip Operates at High Temperature Threshold",
        "description": "Engineers achieve stable topological qubit coherence at 4 Kelvin, dramatically slashing cryogenic cooling infrastructure costs.",
        "content": "Traditional quantum computers require millikelvin dilution refrigerators. Today's peer-reviewed paper demonstrates spin qubits functioning at higher thermal equilibrium, clearing a monumental bottleneck toward commercial modular quantum data centers.",
        "source": "Nature Electronics (Demo)",
        "author": "Dr. Aris Thorne",
        "image_url": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["space-science", "technology"],
        "view_count": 980,
        "engagement_count": 180,
        "hours_ago": 5
    },
    {
        "title": "Central Banks Outline Cross-Border Real-Time Settlement Protocol",
        "description": "Monetary authorities in Asia and Europe pilot instant bilateral settlement rail reducing transaction latency from days to seconds.",
        "content": "Project Agora has finalized its preliminary trial for multilateral wholesale payments. Utilizing synchronized ledger states, the architecture mitigates counterparty risk and currency settlement delays without relying on legacy messaging layers.",
        "source": "Financial Times (Demo)",
        "author": "Sophia Laurent",
        "image_url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["business-economy"],
        "view_count": 2150,
        "engagement_count": 420,
        "hours_ago": 7
    },
    {
        "title": "Zero-Day Vulnerability Patched Across Critical Infrastructure Routers",
        "description": "Cybersecurity agencies issue urgent advisories as hardware vendors release firmware updates mitigating remote memory-corruption flaws.",
        "content": "The vulnerability allowed unauthenticated packet injection into carrier-grade border gateway routers. Security researchers worked with vendors over a 60-day coordinated disclosure period before public exploit proof-of-concepts surfaced.",
        "source": "BleepingComputer (Demo)",
        "author": "Kenji Takahashi",
        "image_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["cybersecurity", "technology"],
        "view_count": 3100,
        "engagement_count": 680,
        "hours_ago": 9
    },
    {
        "title": "Solid-State Battery Production Pilot Reaches Gigawatt Capacity",
        "description": "Automotive battery developers validate 800-mile real-world pack density with rapid 10-minute fast-charging capabilities.",
        "content": "Transitioning from liquid electrolytes to ceramic separators has eliminated thermal runaway hazards. Pilot manufacturing runs demonstrate 98% yield rates, paving the path for mass vehicle deployment beginning next fiscal year.",
        "source": "Electrek (Demo)",
        "author": "Carlos Gomez",
        "image_url": "https://images.unsplash.com/photo-1558441719-74a441366ee9?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["clean-energy-climate", "automotive-ev"],
        "view_count": 1820,
        "engagement_count": 290,
        "hours_ago": 12
    },
    {
        "title": "James Webb Space Telescope Identifies Atmospheric Water on Habitable-Zone Exoplanet",
        "description": "Spectroscopic measurements confirm gaseous signatures in the atmosphere of a super-Earth orbiting an M-dwarf star 48 light-years away.",
        "content": "Infrared transmission spectroscopy revealed pronounced absorption features corresponding to water vapor, methane, and carbon dioxide. The planetary candidate sits firmly within the circumstellar habitable zone.",
        "source": "Astrophysical Journal (Demo)",
        "author": "Dr. Eleanor Vance",
        "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["space-science"],
        "view_count": 4500,
        "engagement_count": 890,
        "hours_ago": 14
    },
    {
        "title": "India Unveils National Semiconductor Fabrication Corridor in Gujarat",
        "description": "Government inaugurates cutting-edge 28nm commercial foundry facility attracting international technology supply chain partners.",
        "content": "The semiconductor cluster aims to meet domestic demand for automotive controllers, power management ICs, and smart grid meters while bolstering global supply chain diversification and high-tech manufacturing capacity.",
        "source": "LiveMint (Demo)",
        "author": "Rajesh Nambiar",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
        "region": "IN",
        "topic_slugs": ["technology", "business-economy"],
        "view_count": 5200,
        "engagement_count": 1150,
        "hours_ago": 16
    },
    {
        "title": "Global Climate Summit Establishes Loss and Damage Climate Resilience Facility",
        "description": "Participating delegates conclude landmark multilateral agreement establishing capital pledges for climate mitigation infrastructure.",
        "content": "Over 120 nations ratified the updated covenant earmarking $150 billion in concessional lending and direct grants targeting coastal defense, drought-resistant agriculture, and renewable decentralized microgrids.",
        "source": "Reuters (Demo)",
        "author": "Amina Al-Mansoor",
        "image_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["clean-energy-climate", "global-politics"],
        "view_count": 1340,
        "engagement_count": 240,
        "hours_ago": 18
    },
    {
        "title": "Breakthrough CRISPR-Cas12 Trial Reverses Hereditary Blindness in Phase 2",
        "description": "Single-dose in vivo gene editing therapy restores retinal photoreceptor signaling in 84% of treated cohort participants.",
        "content": "Clinical investigators reported sustained visual acuity improvements without significant vector-induced inflammation or off-target genomic cleavage. Regulatory fast-track status has been officially requested.",
        "source": "New England Journal of Medicine (Demo)",
        "author": "Dr. Sarah Jenkins",
        "image_url": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["health-biotech", "space-science"],
        "view_count": 2780,
        "engagement_count": 510,
        "hours_ago": 20
    },
    {
        "title": "Championship League Thriller Ends in Stoppage Time Wonder Goal",
        "description": "Dramatic 94th-minute volley secures unforgettable 3-2 victory in continental football clash before a sell-out stadium crowd.",
        "content": "In an electrifying contest featuring relentless end-to-end tactical play, the visitors overcame a two-goal deficit to book their place in the tournament quarterfinals amid jubilant celebrations from traveling supporters.",
        "source": "ESPN Sports (Demo)",
        "author": "Liam Gallagher",
        "image_url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["sports-athletics"],
        "view_count": 3900,
        "engagement_count": 720,
        "hours_ago": 22
    },
    {
        "title": "AI-Powered Diagnostic Imaging Accelerates Early Tumor Detection",
        "description": "Clinical hospital trials demonstrate multi-modal vision transformer algorithms achieving 99.2% sensitivity in mammography screenings.",
        "content": "Radiologists aided by concurrent algorithmic segmentation reduced false-positive callbacks by 34%, ensuring earlier intervention for high-risk patients while lowering unnecessary biopsy procedures.",
        "source": "The Lancet Oncology (Demo)",
        "author": "Dr. Helen Wu",
        "image_url": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["artificial-intelligence", "health-biotech"],
        "view_count": 1650,
        "engagement_count": 340,
        "hours_ago": 24
    },
    {
        "title": "Autonomous Long-Haul Freight Fleet Completes Million-Mile Highway Milestone",
        "description": "Commercial Level-4 freight haulers operate coast-to-coast without safety-driver intervention across diverse weather conditions.",
        "content": "Equipped with redundant lidar, thermal vision, and edge compute neural inference, the automated truck fleet achieved a 100% zero-incident record while optimizing diesel consumption by 11%.",
        "source": "Wired (Demo)",
        "author": "Brett MacIntyre",
        "image_url": "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["automotive-ev", "technology"],
        "view_count": 1220,
        "engagement_count": 190,
        "hours_ago": 26
    },
    {
        "title": "Venture Funding for Clean Hydro-Storage Expands Across South Asia",
        "description": "Pumped-storage hydroelectric assets secure $4.2B in blended finance to stabilize intermittent solar grid over-generation.",
        "content": "As utility-scale solar generation expands exponentially, closed-loop pumped hydro provides crucial 12-hour dispatchable balancing capacity to prevent curtailment during peak daylight hours.",
        "source": "Bloomberg Energy (Demo)",
        "author": "Sunil Nair",
        "image_url": "https://images.unsplash.com/photo-1497440001374-f26997328c1b?auto=format&fit=crop&w=800&q=80",
        "region": "IN",
        "topic_slugs": ["clean-energy-climate", "business-economy"],
        "view_count": 2890,
        "engagement_count": 480,
        "hours_ago": 28
    },
    {
        "title": "Post-Quantum Cryptography Migration Mandates Approved by Global Standards Body",
        "description": "Enterprises instructed to transition PKI infrastructure to lattice-based key encapsulation mechanisms by 2028.",
        "content": "Anticipating 'harvest now, decrypt later' threats from future fault-tolerant quantum algorithms, the standardized Kyber and Dilithium algorithms are now recommended for all TLS and VPN transport layers.",
        "source": "CyberWire (Demo)",
        "author": "Fiona Davies",
        "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["cybersecurity", "technology"],
        "view_count": 1980,
        "engagement_count": 310,
        "hours_ago": 30
    },
    {
        "title": "Olympic Organizing Committee Unveils Carbon-Neutral Stadium Architecture",
        "description": "Timber-framed modular arenas powered entirely by geothermal heat pumps establish new ecological benchmark for mega-sporting events.",
        "content": "Engineers prioritized disassembled reusability, natural ventilation airflow models, and recycled ocean polymer seating across the entire athletic village complex.",
        "source": "BBC Sport (Demo)",
        "author": "Oliver James",
        "image_url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["sports-athletics", "clean-energy-climate"],
        "view_count": 1410,
        "engagement_count": 220,
        "hours_ago": 32
    },
    {
        "title": "Autonomous Drone Fleet Dispatched for Wildlife Anti-Poaching Conservation",
        "description": "AI-guided solar-powered fixed-wing surveillance aircraft monitor endangered rhino populations across expansive national reserves.",
        "content": "Equipped with thermal sensors and onboard edge inference, the autonomous aerial vehicles patrol remote perimeter corridors at night, alerting field ranger teams in real-time to unauthorized human intrusion.",
        "source": "National Geographic (Demo)",
        "author": "Kariuki Mwangi",
        "image_url": "https://images.unsplash.com/photo-1527977966376-1c8408f9f108?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["artificial-intelligence", "space-science"],
        "view_count": 2340,
        "engagement_count": 450,
        "hours_ago": 34
    },
    {
        "title": "Microplastics Filtration Nanomembrane Achieves 99.9% Efficiency in Municipal Water",
        "description": "Biomimetic carbon nanotube filters trap sub-micron microplastic particles without reducing volumetric throughput.",
        "content": "Water purification utilities can retrofit the gravity-fed membrane into existing tertiary treatment stages, preventing synthetic fibers and micro-beads from entering drinking water distribution networks.",
        "source": "Environmental Science Letters (Demo)",
        "author": "Dr. Clara Schmidt",
        "image_url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["space-science", "health-biotech"],
        "view_count": 1890,
        "engagement_count": 320,
        "hours_ago": 36
    },
    {
        "title": "India UPI Digital Transactions Surpass Record Monthly Volume",
        "description": "Unified Payments Interface logs over 15 billion merchant and peer transactions with seamless offline QR tap-and-pay integrations.",
        "content": "The NPCI reported phenomenal adoption in rural and semi-urban markets, driven by voice-assisted conversational banking and cross-border QR interoperability with Southeast Asian trading hubs.",
        "source": "Economic Times (Demo)",
        "author": "Aditi Roy",
        "image_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=800&q=80",
        "region": "IN",
        "topic_slugs": ["business-economy", "technology"],
        "view_count": 6100,
        "engagement_count": 1420,
        "hours_ago": 38
    },
    {
        "title": "Synthetic Biology Startup Produces Industrial Enzymes at One-Tenth Cost",
        "description": "Engineered microbial yeast strains synthesize high-purity detergent and textile processing catalysts via precision fermentation.",
        "content": "By replacing petrochemical-derived catalyst precursors with biological cellular factories, the company demonstrates a closed-loop cradle-to-gate carbon reduction of 72%.",
        "source": "BioTech Today (Demo)",
        "author": "Hugo van der Meer",
        "image_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["health-biotech", "technology"],
        "view_count": 1130,
        "engagement_count": 170,
        "hours_ago": 40
    },
    {
        "title": "Autonomous Lunar Rover Successfully Collects Volatile Ice Samples",
        "description": "South pole exploratory mission confirms subsurface water ice presence within permanently shadowed crater micro-regions.",
        "content": "Using robotic core drilling mechanisms and gas chromatography mass spectrometers, the lander analyzed regolith samples containing bound hydrogen compounds essential for future orbital propellant production.",
        "source": "SpaceFlight Now (Demo)",
        "author": "Astrid Lindholm",
        "image_url": "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["space-science"],
        "view_count": 3890,
        "engagement_count": 760,
        "hours_ago": 42
    },
    {
        "title": "Next-Gen Compiler Uses Reinforcement Learning to Optimize LLVM Bytecode",
        "description": "Compiler engineers integrate deep Q-networks to automate vectorization heuristics and instruction scheduling passes.",
        "content": "Benchmarks across server-side database engines and graphics renderers revealed an 18% execution speedup with 22% reduced binary memory footprint over standard -O3 optimization flags.",
        "source": "ArXiv Computing (Demo)",
        "author": "Devon Harris",
        "image_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["technology", "artificial-intelligence"],
        "view_count": 1560,
        "engagement_count": 280,
        "hours_ago": 44
    },
    {
        "title": "Supply Chain Realignment Drives Industrial Automation Surge",
        "description": "Manufacturing hubs implement collaborative robotic arms and computer vision quality inspection systems to combat labor constraints.",
        "content": "Electronics and precision machinery factories reported record capital expenditure investments into cobots, achieving sub-millimeter tolerances on high-speed surface mount assembly lines.",
        "source": "Wall Street Journal (Demo)",
        "author": "Patricia Miller",
        "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["business-economy", "technology"],
        "view_count": 1740,
        "engagement_count": 310,
        "hours_ago": 46
    },
    {
        "title": "Urban Vertical Agriculture Complex Feeds 100,000 Citizens with 95% Less Water",
        "description": "Hydroponic modular skyscraper facility produces organic leafy greens and strawberries year-round in city center.",
        "content": "Utilizing closed-loop recirculating nutrient systems and adaptive spectral LED lighting, the automated vertical farm eliminates pesticide dependency while shortening food transport miles to zero.",
        "source": "Futurism (Demo)",
        "author": "Zoe Bennett",
        "image_url": "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["clean-energy-climate", "technology"],
        "view_count": 2100,
        "engagement_count": 390,
        "hours_ago": 48
    },
    {
        "title": "Critical Patch Issued for OpenSSL Key Derivation Corner Case",
        "description": "Cryptographic review reveals timing side-channel in specialized ECDSA curves under hyper-threaded CPU environments.",
        "content": "The upstream security team published an emergency release mitigating cache-collision timing leaks. System administrators are urged to apply patches across TLS termination reverse proxies immediately.",
        "source": "Security Affairs (Demo)",
        "author": "Luca Moretti",
        "image_url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["cybersecurity"],
        "view_count": 1870,
        "engagement_count": 340,
        "hours_ago": 50
    },
    {
        "title": "World Chess Championship Blitz Tiebreak Decided on Clock Drama",
        "description": "Reigning grandmaster clinches world crown with split-second pawn promotion under immense two-second increment pressure.",
        "content": "Spectators in attendance witnessed one of the most intense psychological battles in modern chess history as both players navigated 72 moves of razor-sharp tactical complexities with under 10 seconds remaining.",
        "source": "ChessLife (Demo)",
        "author": "Sergei Voronov",
        "image_url": "https://images.unsplash.com/photo-1529699211952-734e80c4d42b?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["sports-athletics"],
        "view_count": 3450,
        "engagement_count": 690,
        "hours_ago": 52
    },
    {
        "title": "Electric Aviation Prototype Completes 500-Mile Regional Flight Trial",
        "description": "Hybrid-electric 19-passenger regional turboprop demonstrates 60% fuel burn reduction on standard commercial route.",
        "content": "Aviation regulatory authorities monitored the historic non-stop regional flight between Portland and Seattle. Low noise signatures and zero ground idling emissions make electric aircraft suitable for urban airfields.",
        "source": "Aviation Week (Demo)",
        "author": "Greg Holbrook",
        "image_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["automotive-ev", "clean-energy-climate"],
        "view_count": 2210,
        "engagement_count": 410,
        "hours_ago": 54
    },
    {
        "title": "Neurotechnology Brain-Computer Interface Translates Inner Speech to Text",
        "description": "Paralyzed participant communicates at 62 words per minute using high-density intracranial microelectrode arrays.",
        "content": "Deep learning decoders trained on motor cortex neural spikes translated imagined words directly into screen text with an astonishing 97% word vocabulary accuracy rate, offering revolutionary autonomy for locked-in patients.",
        "source": "Nature Biotechnology (Demo)",
        "author": "Dr. Miriam O'Connor",
        "image_url": "https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["health-biotech", "artificial-intelligence"],
        "view_count": 4100,
        "engagement_count": 820,
        "hours_ago": 56
    },
    {
        "title": "Global Shipping Alliance Shifts 40 Vessels to Green Methanol Propulsion",
        "description": "Major container shipping consortium commissions retrofitted dual-fuel vessels to reduce trans-oceanic sulfur and carbon footprint.",
        "content": "With green bunkering facilities expanding in Singapore and Rotterdam, the commercial maritime industry accelerates its shift toward e-methanol and bio-ammonia to meet stringent IMO 2030 decarbonization quotas.",
        "source": "Maritime Executive (Demo)",
        "author": "Henrik Nielsen",
        "image_url": "https://images.unsplash.com/photo-1518241353330-0f7941c2d9b5?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["clean-energy-climate", "business-economy"],
        "view_count": 1390,
        "engagement_count": 210,
        "hours_ago": 58
    },
    {
        "title": "Diplomatic Summit Finalizes Antarctic Marine Sanctuary Expansion",
        "description": "38 signatory nations establish protected ecological refuge spanning 1.5 million square kilometers in the Southern Ocean.",
        "content": "The conservation zone permanently prohibits industrial krill harvesting and commercial longline fishing, safeguarding feeding grounds for blue whales, Adelie penguins, and vulnerable polar seabird colonies.",
        "source": "The Guardian (Demo)",
        "author": "Fiona MacLeod",
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["global-politics", "space-science"],
        "view_count": 2980,
        "engagement_count": 540,
        "hours_ago": 60
    },
    {
        "title": "High-Efficiency Perovskite Tandem Solar Cell Achieves 33.9% Certified Efficiency",
        "description": "Laboratory breakthrough in silicon-perovskite interface passivation shatters theoretical single-junction Shockley-Queisser limit.",
        "content": "Damp-heat stability testing validated over 1,500 hours of continuous outdoor illumination without degradation. Scalable roll-to-roll vapor deposition techniques are currently under licensing negotiations with global panel manufacturers.",
        "source": "Solar Energy Materials (Demo)",
        "author": "Dr. Chen Wei",
        "image_url": "https://images.unsplash.com/photo-1508873696983-2df5293cb32b?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["clean-energy-climate", "technology"],
        "view_count": 3150,
        "engagement_count": 630,
        "hours_ago": 62
    },
    {
        "title": "India ISRO Launches Advanced Weather and Ocean Observation Satellite",
        "description": "Geosynchronous satellite INSAT-4DS successfully deployed to monitor storm formation and monsoon precipitation patterns.",
        "content": "From the Sriharikota launch pad, the multi-stage GSLV rocket placed the 2,275-kilogram meteorological satellite into precise geostationary orbit, significantly enhancing cyclone warning lead times across the Indian Ocean rim.",
        "source": "ISRO News (Demo)",
        "author": "K. Sivanath",
        "image_url": "https://images.unsplash.com/photo-1516849841032-87cbac4d88f7?auto=format&fit=crop&w=800&q=80",
        "region": "IN",
        "topic_slugs": ["space-science", "technology"],
        "view_count": 5800,
        "engagement_count": 1320,
        "hours_ago": 64
    },
    {
        "title": "Marathon World Record Shattered at Valencia Road Race",
        "description": "Elite distance runner clocks historic 1:59:45 in official competition utilizing biomechanically tuned carbon-plated footwear.",
        "content": "Under ideal 12-degree Celsius morning conditions, the pacemaker squad executed textbook negative splits, guiding the champion to a historic sub-two-hour finish celebrated by thousands along the finish straightaway.",
        "source": "Runner's World (Demo)",
        "author": "Mark O'Shaughnessy",
        "image_url": "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?auto=format&fit=crop&w=800&q=80",
        "region": "GLOBAL",
        "topic_slugs": ["sports-athletics"],
        "view_count": 4200,
        "engagement_count": 890,
        "hours_ago": 66
    }
]

def seed_database(db: Session, force: bool = False):
    """
    Seeds realistic demo data into the database.
    Idempotent: skips if data already exists, unless force=True.
    """
    existing_users = db.query(User).count()
    if existing_users > 0 and not force:
        logger.info("Database already seeded with demo data. Skipping.")
        return

    logger.info("Beginning database seeding...")

    # 1. Seed Topics
    topic_map = {}
    for t_data in DEMO_TOPICS:
        existing = db.query(Topic).filter(Topic.slug == t_data["slug"]).first()
        if not existing:
            topic = Topic(name=t_data["name"], slug=t_data["slug"])
            db.add(topic)
            db.flush()
            topic_map[t_data["slug"]] = topic
        else:
            topic_map[t_data["slug"]] = existing

    # 2. Seed Users
    user_map = {}
    for u_data in DEMO_USERS:
        existing = db.query(User).filter(User.username == u_data["username"]).first()
        if not existing:
            user = User(id=u_data["id"], username=u_data["username"], email=u_data["email"])
            db.add(user)
            db.flush()
            user_map[u_data["id"]] = user
        else:
            user_map[u_data["id"]] = existing

    # 3. Seed Articles
    now = datetime.utcnow()
    article_entities = []
    for art in DEMO_ARTICLES:
        existing = db.query(Article).filter(Article.title == art["title"]).first()
        if not existing:
            pub_date = now - timedelta(hours=art.get("hours_ago", 1))
            article = Article(
                title=art["title"],
                description=art["description"],
                content=art["content"],
                source=art["source"],
                author=art["author"],
                image_url=art["image_url"],
                region=art["region"],
                view_count=art["view_count"],
                engagement_count=art["engagement_count"],
                published_at=pub_date,
                created_at=pub_date
            )
            db.add(article)
            db.flush()

            for slug in art["topic_slugs"]:
                if slug in topic_map:
                    at = ArticleTopic(article_id=article.id, topic_id=topic_map[slug].id)
                    db.add(at)
            article_entities.append(article)

    # 4. Seed User Follows
    # User 101 (Alex Chen) follows: AI, Technology, Cybersecurity
    # User 102 (Priya Sharma) follows: Business & Economy, Clean Energy & Climate, Technology
    # User 103 (David Miller) follows: Sports & Athletics, Space & Science
    user_topic_pairs = [
        (101, "artificial-intelligence"),
        (101, "technology"),
        (101, "cybersecurity"),
        (102, "business-economy"),
        (102, "clean-energy-climate"),
        (102, "technology"),
        (103, "sports-athletics"),
        (103, "space-science")
    ]

    for uid, tslug in user_topic_pairs:
        if tslug in topic_map and uid in user_map:
            tid = topic_map[tslug].id
            existing = db.query(UserTopic).filter(UserTopic.user_id == uid, UserTopic.topic_id == tid).first()
            if not existing:
                db.add(UserTopic(user_id=uid, topic_id=tid, followed_at=now - timedelta(days=1)))

    # 5. Seed Welcome Notifications for users
    for uid in [101, 102, 103]:
        db.add(Notification(
            user_id=uid,
            message="Welcome to your Personalized News Platform! Follow topics to curate your daily feed.",
            status="unread",
            created_at=now - timedelta(hours=3)
        ))

    db.commit()
    logger.info("Successfully seeded database with 32 realistic articles, 10 topics, 4 users, and preferences.")
