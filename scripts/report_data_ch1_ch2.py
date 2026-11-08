# report_data_ch1_ch2.py
"""
Chapter 1 (Introduction) and Chapter 2 (Literature Survey) content
for the Mohan Babu University (MBU) TESP Project Report.
Exhaustive, rigorous academic prose formatted with proper spacing and separated lists.
"""

CH1_INTRO = [
    (
        "Urban drainage systems are vital municipal infrastructure assets designed to convey surface runoff away from residential, "
        "commercial, and transit corridors into natural river basins or receiving water bodies. In recent decades, rapid urbanization, "
        "uncontrolled concretization, and climate change-induced high-intensity precipitation events have combined to overwhelm aging storm "
        "drainage networks across developing cities worldwide. When precipitation exceeds the hydraulic conveyance capacity of urban nallahs, "
        "culverts, and storm canals, surface water rapidly accumulates, resulting in severe urban flash flooding. Unlike gradual riverine "
        "flooding, urban flash floods occur within minutes or hours of extreme rainfall, giving municipal authorities and vulnerable citizens "
        "minimal preparation time. The consequences are catastrophic: submerged roadways, crippled transit underbridges, contaminated water "
        "supplies, severe structural damage to homes and businesses, and tragic loss of human life."
    ),
    (
        "Traditional flood monitoring in developing municipal jurisdictions has historically relied on manual inspections, static staff gauges, "
        "and delayed public emergency broadcasts through television or radio. Such legacy approaches exhibit major operational shortcomings. "
        "Manual measurements cannot be conducted safely during torrential downpours, staff gauges provide no telemetry to centralized command "
        "centers, and broadcast announcements lack localized geographic precision. Furthermore, drainage floodgates in urban culverts are often "
        "manually operated by field crews who must physically travel to inundated sites during severe weather—often arriving long after the "
        "culvert has been overtopped and nearby neighborhoods have flooded. In the worst scenarios, upstream gates remain open, permitting "
        "mountain runoff to surge into clogged urban basins, or downstream backflow gates fail to shut, allowing swollen rivers to reverse "
        "into city streets."
    ),
    (
        "The emergence of the Internet of Things (IoT), edge microcontrollers, low-power telemetry sensors, and high-performance cloud "
        "computing architectures presents a transformative paradigm for urban flood management. By instrumenting vulnerable storm drainage "
        "flashpoints with autonomous, sensor-equipped microcontrollers, cities can continuously measure water depths, calculate flood rise "
        "rates, actuate emergency floodgates locally without relying on distant cloud servers, and instantly stream hydrological data to "
        "municipal command centers. Furthermore, by coupling real-time telemetry with geospatial graph routing algorithms, early warning "
        "systems can dynamically direct fleeing citizens toward the nearest safe relief shelters along roads guaranteed to avoid flooded "
        "drainage junctions. This project, titled 'flood-ews' (Smart Community Flood & Urban Drainage Early Warning System), addresses this "
        "pressing societal challenge through an integrated, cyber-physical edge-to-cloud architecture designed and validated specifically "
        "for the complex urban catchment dynamics of Tirupati, India."
    ),
]

CH1_REGIONAL_ANALYSIS = [
    (
        "Tirupati, situated at the base of the Seshachalam hill ranges in the Rayalaseema region of Andhra Pradesh, represents a classic "
        "high-risk foothill urban catchment. The city sits within the Swarnamukhi River basin, characterized by a dramatic elevation drop "
        "from the Tirumala sacred hills (over 850 meters above mean sea level) down to the urban plains (approximately 150 meters above mean sea level) "
        "across a horizontal span of less than 10 kilometers. During the Northeast monsoon (October–December) and cyclonic depressions originating "
        "in the Bay of Bengal, the Seshachalam hills receive intense, convective cloudbursts. The steep granite slopes possess near-zero soil "
        "retention, causing rapid surface runoff to cascade violently into natural mountain streams (nallahs) that terminate abruptly in the "
        "densely populated municipal wards of Tirupati."
    ),
    (
        "Several critical flashpoints along the Swarnamukhi foothill channels routinely experience sudden inundation. The most hazardous "
        "is Kapilatheertham Nallah, where mountain runoff funnels directly from the Kapilatheertham waterfalls into the Alipiri urban sector. "
        "Downstream, the runoff converges with municipal drainage canals at Leela Mahal Culvert and the Korlagunta Storm Canal. Critical transit "
        "arteries, such as the Railway Underbridge (West) near Tata Nagar, suffer from chronic drainage choking due to low road depressions and "
        "sediment accumulation. At the southern municipal boundary, the Tiruchanur Swarnamukhi Causeway faces backwater surges whenever the "
        "main river swells. Table 1.1 documents the 6 primary drainage flashpoints instrumented in this project, including geospatial "
        "coordinates, cross-sectional drainage capacities, mount heights, and local municipal wards."
    ),
]

TABLE_1_1_DATA = [
    ["drain-01", "Kapilatheertham Nallah", "13.6508° N", "79.4215° E", "Alipiri", "200.0 cm", "180.0 cm", "Direct Seshachalam foothill runoff from waterfall chasm"],
    ["drain-02", "Leela Mahal Culvert", "13.6370° N", "79.4285° E", "Korlagunta", "220.0 cm", "200.0 cm", "High-density commercial arterial culvert convergence"],
    ["drain-03", "Railway Underbridge (West)", "13.6255° N", "79.4205° E", "Tata Nagar", "180.0 cm", "150.0 cm", "Low-lying road depression beneath railway main line"],
    ["drain-04", "Korlagunta Storm Canal", "13.6330° N", "79.4350° E", "Korlagunta", "210.0 cm", "190.0 cm", "Primary urban stormwater discharge canal to Swarnamukhi"],
    ["drain-05", "Alipiri Footpath Channel", "13.6450° N", "79.4070° E", "Alipiri", "190.0 cm", "160.0 cm", "Pilgrim pedestrian corridor runoff conduit at ghat road base"],
    ["drain-06", "Tiruchanur Swarnamukhi Causeway", "13.6095° N", "79.4505° E", "Tiruchanur", "230.0 cm", "210.0 cm", "Submersible causeway crossing Swarnamukhi river channel"],
]

CH1_PROBLEM_STATEMENT = [
    (
        "Despite recurring seasonal floods that disrupt public transit, damage infrastructure, and threaten human safety across Tirupati and "
        "similar foothill cities, urban drainage monitoring remains severely constrained by four critical systemic deficiencies:"
    ),
]

CH1_PROBLEM_ITEMS = [
    "Lack of Automated High-Frequency Hydrological Telemetry: Municipal drainage authorities rely on delayed manual field reports rather than continuous, real-time depth and rise-rate measurements. As a consequence, localized inundation at culverts and underpasses is frequently recognized only after road submergence has already paralyzed vehicular traffic.",
    "Absence of Autonomous Edge Failsafe Actuation: Existing stormwater gates require manual crank operation or cloud-dependent relays. During severe cyclonic storms, cellular towers and municipal internet infrastructure frequently experience brownouts or complete failure. When cloud connectivity is lost, conventional remote-controlled gates freeze in place, leaving upstream floodwaters unchecked and downstream communities exposed to backflow surges.",
    "Static, Non-Adaptive Evacuation Guidance: Conventional municipal disaster plans publish static emergency evacuation routes on paper or municipal websites. These static routes fail to account for dynamic, real-time flood conditions. A citizen following a static evacuation map may unknowingly be directed straight toward an inundated railway underpass or overflowing culvert, turning an evacuation attempt into a deadly hazard.",
    "Monolingual and Delayed Public Alerting: Emergency broadcasts are predominantly issued in English or through standard bureaucratic press bulletins. Vulnerable citizens in low-lying wards—many of whom are native Telugu or Hindi speakers—do not receive actionable, real-time warnings on their everyday mobile devices (such as SMS and WhatsApp) with clear directions in their native language.",
]

CH1_OBJECTIVES_INTRO = (
    "To systematically address the aforementioned engineering and societal challenges, the primary objectives of this TESP project are:"
)

CH1_OBJECTIVES_ITEMS = [
    "To design and build an autonomous, edge-computing IoT sensor node based on the ESP32 microcontroller, integrating non-contact ultrasonic depth sensing, real-time depth calculation, localized audiovisual alarms, and automated servo-driven floodgate actuation.",
    "To engineer an edge-level failsafe control algorithm that enables the ESP32 to autonomously evaluate water depth thresholds (Warning at 70% capacity, Critical at 85% capacity) and close emergency floodgates within milliseconds, operating with 100% autonomy even during total cloud or network communication blackouts.",
    "To implement a lightweight, robust telemetry communication architecture using Message Queuing Telemetry Transport (MQTT) with Quality of Service (QoS) Level 1, streaming live hydrological data, gate angles, and device health to cloud brokers with sub-second latency.",
    "To build a high-performance, asynchronous cloud backend utilizing FastAPI and TimescaleDB hypertables, capable of persisting high-frequency time-series telemetry, calculating 5-minute continuous aggregates, and evaluating multi-tier flood risk through a 3-tick hysteresis engine that eliminates false alarm oscillations.",
    "To develop a dynamic, flood-aware evacuation routing service utilizing Dijkstra's shortest path algorithm with adaptive risk-penalized edge weights, automatically guiding citizens away from flooded drain nodes toward the nearest available disaster relief shelter.",
    "To create an automated, multilingual notification gateway delivering instant localized SMS and WhatsApp alerts in Telugu, Hindi, and English, complete with one-click dynamic evacuation routing links.",
    "To validate the end-to-end cyber-physical system across simulated and hardware environments, verifying edge actuation latency, cloud telemetry delivery, Dijkstra route convergence, and comprehensive unit/integration test suite reliability.",
]

CH1_SCOPE = (
    "The project encompasses the end-to-end design, implementation, and empirical verification of the cyber-physical flood early warning "
    "system. This includes hardware component selection, circuit schematic design, embedded C++ and MicroPython firmware development, MQTT "
    "broker orchestration, asynchronous Python backend service creation, PostgreSQL/TimescaleDB time-series database modeling, Dijkstra "
    "routing graph formulation, multilingual template localization, and dual Next.js web application development (an Operator SCADA "
    "Command Center and a Public Citizen Evacuation Portal). The spatial scope is modeled upon the 6 critical drainage flashpoints and 4 "
    "designated disaster relief camps of Tirupati Municipal Corporation."
)

CH1_APPLICATIONS_INTRO = (
    "The engineered system offers direct, high-impact applications across municipal governance, disaster resilience, and citizen safety:"
)

CH1_APPLICATIONS_ITEMS = [
    "Municipal Smart City Operations: Provides city engineers with a real-time SCADA dashboard to visualize drainage levels across all urban wards.",
    "Autonomous Flash Flood Prevention: Edge floodgates automatically seal low-lying culverts to prevent river backflow into residential zones.",
    "Smart Transit Management: Automated road warnings at railway underpasses prevent vehicle submergence and passenger fatalities.",
    "Citizen Disaster Evacuation: Dispatches immediate, localized evacuation paths directly to citizens' mobile phones in their native languages.",
    "Hydrological Data Science: Accumulated TimescaleDB historical data enables civil engineers to calibrate hydraulic drainage models and plan long-term infrastructure upgrades.",
]

CH1_LIMITATIONS_INTRO = (
    "While highly effective, the current system implementation exhibits the following operational constraints:"
)

CH1_LIMITATIONS_ITEMS = [
    "Ultrasonic Sensor Environmental Interference: The HC-SR04 ultrasonic transducer relies on acoustic echo time-of-flight, which can be affected by extreme air temperature fluctuations, heavy steam, or dense floating debris on the water surface.",
    "Wi-Fi Range Constraints: The ESP32 nodes utilize 2.4 GHz IEEE 802.11 b/g/n Wi-Fi, necessitating local gateways or cellular hotspots within 50–100 meters of each drainage culvert.",
    "Cloud Notification Dependencies: While edge gate actuation is 100% autonomous and offline-capable, public WhatsApp and SMS notification dispatch requires upstream Internet and telecom gateway connectivity.",
]

CH2_LITERATURE_SURVEY = [
    (
        "2.1 Evolution of Urban Drainage and Flood Monitoring Systems",
        [
            (
                "Early warning systems for hydrological disasters have evolved through three distinct technological eras over the past half-century. "
                "In the first era (1970s–1990s), municipal monitoring relied entirely on physical human reconnaissance and mechanical staff gauges installed "
                "at riverbanks. These systems suffered from severe human latency: during nocturnal torrential rains, inspection crews could not safely traverse "
                "flooded roads, resulting in warnings that were broadcast hours after neighbourhoods were already inundated (Smith et al., 1998)."
            ),
            (
                "The second era (2000s–2010s) witnessed the introduction of automated Supervisory Control and Data Acquisition (SCADA) systems and "
                "satellite radar altimetry. While satellite radar (e.g., Sentinel and Landsat) provides valuable regional flood mapping, its temporal "
                "revisit intervals (typically 5 to 12 days) and cloud-cover occlusion render it entirely ineffective for rapid urban flash floods, which develop "
                "and recede within hours (Bates, 2012). Traditional municipal SCADA systems, meanwhile, relied on expensive, proprietary industrial PLCs and "
                "dedicated leased lines, resulting in exorbitant deployment costs ($15,000 to $50,000 per monitoring station) that prohibited dense spatial "
                "instrumentation across municipal nallahs in developing nations (Moy de Perez et al., 2017)."
            ),
            (
                "The modern third era is defined by low-cost Internet of Things (IoT) microcontrollers, wireless sensor networks (WSNs), and distributed "
                "cloud computing. Contemporary research demonstrates that dense networks of low-cost IoT nodes provide superior spatial granularity, "
                "enabling hyper-local flood detection at a fraction of the cost of industrial SCADA installations (Kaur & Sood, 2020)."
            ),
        ]
    ),
    (
        "2.2 Wireless Sensor Networks and Hydrological Telemetry",
        [
            (
                "Selecting appropriate water level sensing transducers is critical for reliable hydrological telemetry. Extant literature categorizes liquid "
                "level transducers into contact-based and non-contact transducers. Contact-based sensors, such as submerged hydrostatic pressure probes and "
                "resistive float switches, are subject to rapid bio-fouling, silt encrustation, and physical destruction from floating debris, tree limbs, "
                "and urban solid waste carried by torrential flood currents (Ancona et al., 2014)."
            ),
            (
                "Consequently, non-contact transducers—specifically ultrasonic and millimeter-wave radar sensors—have emerged as the prevailing standard. "
                "Ultrasonic transducers (such as the HC-SR04 and JSN-SR04T) measure the acoustic time-of-flight of an ultrasonic pulse (typically 40 kHz) "
                "reflected off the water surface. The distance d is determined by the fundamental physical relationship:\n\n"
                "d = (v_sound * t) / 2\n\n"
                "where v_sound is approximately 343 m/s at 20°C and t is the elapsed round-trip propagation time. By fixing the sensor at a known mount "
                "height H_mount above the drainage bed, instantaneous water depth is computed as D = H_mount - d. Recent studies by Al-Dahoud et al. (2021) "
                "and Silva et al. (2022) confirm that ultrasonic sensors provide millimeter-level depth resolution when mounted within 0.2 to 4.0 meters of "
                "urban drainage channels, offering an optimal balance between sensing accuracy, low power consumption (under 15 mA), and component affordability."
            ),
        ]
    ),
    (
        "2.3 Edge Computing and Autonomous Failsafe Actuation in Drainage",
        [
            (
                "A critical vulnerability identified in contemporary IoT flood monitoring literature is the pervasive over-reliance on cloud-centric "
                "decision architectures. In standard cloud-IoT designs, microcontrollers merely transmit raw sensor data to distant cloud servers, which "
                "process the data, evaluate risk thresholds, and transmit actuation commands back to physical floodgates (Babu et al., 2019)."
            ),
            (
                "However, empirical disaster studies reveal that extreme storm events are precisely when cellular base stations, fiber-optic backbones, and "
                "power grids experience catastrophic disruption (Kumar & Pathak, 2021). A cloud-dependent floodgate cannot receive actuation commands during a "
                "network brownout. If a culvert gate freezes in the open position, backflow surges submerge nearby residential settlements. The edge computing "
                "paradigm shifts the critical actuation logic directly into the microcontroller firmware. By executing a local Finite State Machine (FSM) on "
                "the ESP32, the edge node evaluates depth thresholds and commands servo motor horns to seal floodgates within milliseconds, operating with total "
                "autonomy regardless of cloud connectivity status (Shi et al., 2016; Satyanarayanan, 2017)."
            ),
        ]
    ),
    (
        "2.4 Communication Protocol Comparison: MQTT vs. HTTP/REST in Emergency Telematics",
        [
            (
                "Telemetric communication protocols dictate the energy efficiency, bandwidth utilization, and transmission latency of IoT field nodes. The two "
                "dominant protocols investigated in literature are Hypertext Transfer Protocol (HTTP/REST) and Message Queuing Telemetry Transport (MQTT). "
                "HTTP is a request-response protocol running over TCP, requiring substantial header overhead (typically 200–800 bytes per request) and "
                "repetitive TCP three-way handshakes and TLS negotiations for each sensor reading. In contrast, MQTT is an extremely lightweight "
                "publish-subscribe protocol designed specifically for constrained telemetry over unreliable networks (Banks & Gupta, 2014)."
            ),
        ]
    ),
]

CH2_MQTT_TIERS_INTRO = "MQTT provides three distinct Quality of Service (QoS) delivery tiers for IoT applications:"
CH2_MQTT_TIERS = [
    "QoS 0 (At most once): Best-effort delivery without acknowledgment; packets may be lost during network drops.",
    "QoS 1 (At least once): Guaranteed delivery with cryptographic packet identifier acknowledgment (PUBACK); packets are retransmitted until received.",
    "QoS 2 (Exactly once): Four-step handshake ensuring zero duplication, but introducing higher latency.",
]
CH2_MQTT_CONCLUSION = (
    "Comparative benchmark studies by Yassein et al. (2017) and Mishra & Kertesz (2020) demonstrate that MQTT QoS 1 achieves up to 93% less network "
    "overhead and 10-times lower latency compared to HTTP POST requests under weak 2G/3G cellular links, making MQTT the definitive protocol for "
    "mission-critical flood telemetry."
)

CH2_REMAINING_SECTIONS = [
    (
        "2.5 Time-Series Data Management & Continuous Aggregates",
        [
            (
                "High-frequency IoT drainage monitoring produces enormous volumes of time-stamped telemetry data. A municipal network of 6 nodes publishing "
                "telemetry every 3 seconds generates over 172,000 records daily. Conventional relational database management systems (RDBMS) like MySQL and "
                "vanilla PostgreSQL experience severe performance degradation when querying millions of time-series rows, as B-tree indices expand beyond "
                "available RAM and require expensive disk read operations (Freedman et al., 2018)."
            ),
            (
                "TimescaleDB, an open-source time-series extension engineered for PostgreSQL, resolves this scalability barrier through automated time-and-space "
                "partitioning known as 'hypertables'. Hypertables partition data into discrete chunks based on timestamps, ensuring that active ingestion chunks "
                "fit entirely within CPU cache and memory buffers. Furthermore, TimescaleDB continuous aggregates automatically pre-compute 5-minute statistical "
                "rollups (minimum, maximum, average depths, and sample counts) in background worker threads, allowing historical analytical queries spanning "
                "months to execute in milliseconds without impacting real-time telemetry ingestion (Duggan et al., 2015)."
            ),
        ]
    ),
    (
        "2.6 Dynamic Graph Routing and Evacuation Navigation",
        [
            (
                "Public evacuation routing during flash floods is a complex multi-objective optimization problem. Traditional emergency evacuation plans "
                "rely on static route maps that assume all municipal roadways remain traversable during a crisis. However, flood studies by Dawson et al. "
                "(2011) and Pyatkova et al. (2019) emphasize that urban inundation is spatially dynamic and non-uniform: low-lying underpasses and bridge "
                "approaches flood rapidly while elevated ridge roads remain dry."
            ),
            (
                "To provide safe navigation, early warning systems must model the urban road network as a directed weighted graph G = (V, E), where vertices "
                "V represent road intersections, relief shelters, and drainage flashpoints, and edges E represent road segments. Dijkstra's shortest "
                "path algorithm computes the minimum-cost path from an origin vertex to a destination shelter. By dynamically modulating edge weights based on "
                "real-time flood telemetry—assigning prohibitive penalty multipliers to edges traversing drain nodes in WARNING or CRITICAL states—the routing "
                "engine dynamically guides evacuees around submerged corridors along provably safe paths (Yuan & Wang, 2018)."
            ),
        ]
    ),
    (
        "2.7 Multilingual Emergency Alerting Frameworks",
        [
            (
                "The ultimate efficacy of any early warning system depends upon human compliance and rapid behavioral response. Socio-hydrological research "
                "by Mileti & Sorensen (1990) and Wood et al. (2012) identifies language barriers and message ambiguity as primary causes of evacuation "
                "failure during municipal disasters. In multilingual nations like India, emergency alerts issued solely in English or official national "
                "languages fail to reach high-risk populations residing in vulnerable informal settlements along drainage nallahs."
            ),
            (
                "Furthermore, modern citizens overwhelmingly consume real-time information via mobile messaging applications rather than broadcast media. "
                "Integrating carrier-grade Short Message Service (SMS) gateways and the WhatsApp Business API enables early warning systems to push localized, "
                "native-language alerts (e.g., Telugu and Hindi) directly into citizens' pockets. Incorporating direct, one-click evacuation web links within the "
                "message empowers citizens to open dynamic turn-by-turn navigation on their smartphones without requiring prior app installations."
            ),
        ]
    ),
]

CH2_RESEARCH_GAPS_INTRO = "A rigorous synthesis of the reviewed literature reveals four profound research and engineering gaps:"
CH2_RESEARCH_GAPS = [
    "Gap 1: Existing academic flood IoT prototypes focus exclusively on cloud data visualization, omitting localized autonomous edge failsafe actuation mechanisms capable of operating during network collapse.",
    "Gap 2: Telemetry systems treat risk thresholds as static scalars, lacking rate-of-rise dynamic evaluation and hysteresis dampening, which leads to severe false alarm oscillations.",
    "Gap 3: Evacuation planning tools operate independently of live drainage telemetry, failing to compute dynamic, hazard-avoiding detour paths.",
    "Gap 4: Public alerting systems lack automated multilingual dispatch integrated with personalized mobile messaging gateways.",
]
CH2_RESEARCH_GAPS_CONCLUSION = "The flood-ews architecture developed in this project directly bridges these four critical gaps into a unified, cyber-physical platform."

TABLE_2_1_DATA = [
    ["Traditional Manual SCADA", "Mechanical Float / Staff", "Leased Line / RS-485", "Central PLC Server", "None (Manual Field Crew)", "No", "Relational RDBMS", "Static sirens", "Exorbitant ($25k+)"],
    ["Satellite Radar Remote Sensing", "Synthetic Aperture Radar", "Downlink Satellite", "Cloud Data Center", "None", "No", "Spatial Raster Files", "Regional Bulletins", "Extreme (Govt Agency)"],
    ["Cloud-Centric IoT Prototype", "Ultrasonic (HC-SR04)", "HTTP REST / Wi-Fi", "Cloud VM", "Cloud Relay (Fails on outage)", "No", "MySQL / MongoDB", "Monolingual SMS", "Low ($50)"],
    ["Proposed flood-ews Platform", "Ultrasonic + Edge ESP32", "MQTT QoS 1 + HiveMQ", "FastAPI + Edge FSM", "Autonomous Edge Servo + Cloud Override", "Yes (Dijkstra)", "TimescaleDB Hypertables", "Multilingual SMS + WhatsApp", "Very Low ($25/node)"],
]
