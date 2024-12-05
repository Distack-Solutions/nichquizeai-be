import json


# Input JSON string
json_string = '''{"title": "Wellness Roadmap","description": "Thank you for taking this quiz! Your answers help us guide you on your wellness journey. This roadmap is designed to give you personalized insights and recommendations based on your quiz results.","performance_analytics": [{
      "param_name": "Sleep Quality",
      "param_description": "Measures how well you are sleeping, including sleep duration and consistency.",
      "score": {
        "value": 75,
        "max_value": 100
      }
    },
    {
      "param_name": "Stress Level",
      "param_description": "Assesses the level of stress you experience in your daily life, considering both mental and physical stressors.",
      "score": {
        "value": 55,
        "max_value": 100
      }
    }
  ],
  "sections": [
    {
      "title": "Improving Sleep Quality",
      "steps": [
        {
          "title": "Set a Consistent Sleep Schedule",
          "description": "Going to bed and waking up at the same time each day helps regulate your body's internal clock."
        },
        {
          "title": "Create a Relaxing Bedtime Routine",
          "description": "Engage in activities like reading or meditating to calm your mind before bed."
        },
        {
          "title": "Limit Caffeine and Screen Time",
          "description": "Avoid caffeine and screen exposure at least an hour before going to bed to improve sleep quality."
        },
        {
          "title": "Optimize Your Sleep Environment",
          "description": "Ensure your bedroom is quiet, dark, and cool to enhance sleep comfort."
        }
      ]
    },
    {
      "title": "Managing Stress",
      "steps": [
        {
          "title": "Practice Mindfulness and Meditation",
          "description": "Incorporate mindfulness techniques to help you stay calm and focused during stressful situations."
        },
        {
          "title": "Exercise Regularly",
          "description": "Physical activity can significantly reduce stress levels and improve your overall well-being."
        },
        {
          "title": "Stay Connected with Supportive People",
          "description": "Reach out to family and friends who can offer support and help you manage stress."
        },
        {
          "title": "Set Boundaries and Prioritize Tasks",
          "description": "Learning to say no and managing your time effectively can reduce stress caused by overcommitment."
        }
      ]
    }
  ],
  "insights": [
    {
      "insight": "Your sleep quality is good, but making a few adjustments can help you feel more rested and energized each day."
    },
    {
      "insight": "Reducing stress is essential to maintaining both your mental and physical health. Taking time for self-care is crucial."
    }
  ],
  "product_recommendation": [
    {
      "product_key": "sleep_therapy",
      "benefits": [
        "Helps improve sleep duration and quality",
        "Reduces anxiety and promotes relaxation before bed"
      ],
      "usage_instructions": "Use this product an hour before bedtime to unwind and relax. Pair it with a consistent bedtime routine for best results."
    },
    {
      "product_key": "stress_relief",
      "benefits": [
        "Reduces feelings of tension and anxiety",
        "Improves mental clarity and focus"
      ],
      "usage_instructions": "Take this product during times of high stress to help calm your mind and maintain focus."
    }
  ],
  "encouragement": "You are on the right path! Continue making these small changes, and you will see great improvements in your overall well-being. Stay motivated and keep pushing forward!"
}
'''

# List of root-level keys to check for completion
root_keys = [
    "title", 
    "description",
    "performance_analytics",
    "sections",
    "insights",
    "product_recommendation",
    "encouragement"
]
root_structure = {}

# Function to print the structure as soon as a root key is completed
def print_json_when_complete():
    print("=========")
    print(json.dumps(root_structure, indent=2))
    print("=========")

# Processing the JSON in chunks
chunk_size = 1
current_chunk = ""
completed_keys = set()

# Iterate through the JSON string in chunks
for i in range(0, len(json_string), chunk_size):
    current_chunk += json_string[i:i + chunk_size]
    # Attempt to load the current chunk as JSON
    try:
        parsed_json = json.loads(current_chunk)
        
        # Update the root structure if any root key is found
        for key in root_keys:
            if key in parsed_json and key not in completed_keys:
                root_structure[key] = parsed_json[key]
                completed_keys.add(key)
                # Print the JSON once the key is completed
                # print_json_when_complete()
                print(root_structure.keys())

    except json.JSONDecodeError:
        # If the chunk doesn't form valid JSON, continue adding more chunks
        pass
