from app import app, db, Category

categories = [
    ("False Urgency", "#EF9F27"),
    ("Hidden Costs", "#E24B4A"),
    ("Forced Consent", "#D4537E"),
    ("Misleading Wording", "#D85A30"),
    ("Hard to Cancel", "#378ADD"),
    ("Social Pressure", "#639922"),
]

with app.app_context():
    for name, color in categories:
        # Skip if this category already exists (avoid duplicates)
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name, color=color))
    db.session.commit()
    print("Categories inserted:")
    for c in Category.query.all():
        print(f"  {c.id}. {c.name} ({c.color})")
