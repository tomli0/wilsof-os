.pragma library

var profiles = [
    {id: "clean", name: "CLEAN", icon: "material:check_box_outline_blank"},
    {id: "study", name: "STUDY", icon: "material:school"},
    {id: "development", name: "DEV", icon: "material:terminal"},
    {id: "everyday", name: "EVERYDAY", icon: "material:home"}
];

function valid(profile) {
    return profiles.some(p => p.id === profile);
}

function name(profile) {
    const p = profiles.find(p => p.id === profile);
    return p ? p.name : "PROFIL";
}

function label(state) {
    return state && state.applied && !state.error
        ? name(state.applied) : name(state ? state.saved : null) + " · ?";
}

function items(query, state) {
    var q = (query || "").trim().toLowerCase();
    // General app search stays uncluttered. The bar already opens "profil";
    // explicit profile names remain fast keyboard entry points.
    if (/^profil(?:e)?(?:\s|$)/.test(q))
        q = q.replace(/^profil(?:e)?\s*/, "");
    else if (!profiles.some(p => p.id === q || p.name.toLowerCase() === q))
        return [];
    return profiles.map(p => ({
        name: "Profil · " + p.name,
        icon: p.icon,
        comment: state && state.error
            ? "Feil · " + state.error
            : state && state.applied === p.id
                ? "Aktiv · ingen apper flyttes eller lukkes"
                : "Velg profil · ingen apper startes automatisk",
        action: p.id,
        categories: ["Wilsof-profiler"]
    })).filter(i => !q || (i.name + " " + i.action + " profile").toLowerCase().includes(q));
}
