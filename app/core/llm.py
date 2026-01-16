from openai import OpenAI
from app.core.config import config

class LLMClient:
    def __init__(self):
        if not config:
            raise RuntimeError("Configuration not loaded.")
        
        self.client = OpenAI(
            base_url=config.llm.base_url,
            api_key=config.llm.api_key
        )
        self.model = config.llm.model
        self.character = config.character

    def generate_response(self, visitor_name: str, message: str, context: list[dict] = None, relationship_context: str = None) -> str:
        """
        Generates a response from the host character.
        """
        system_prompt = ""
        
        # Check for Active Card
        if self.character.active_card_id:
            try:
                from app.core.database import engine, CharacterCard
                from sqlmodel import Session
                with Session(engine) as session:
                    card = session.get(CharacterCard, self.character.active_card_id)
                    if card:
                         system_prompt = (
                             f"You are {card.name}.\n"
                             f"[Description]\n{card.description}\n"
                             f"[Personality]\n{card.personality}\n"
                             f"[Scenario]\n{card.scenario}\n"
                             f"[Message Examples]\n{card.mes_example}\n"
                             f"{card.system_prompt or ''}\n"
                         )
                         if self.character.persona:
                             system_prompt += f"\n[Additional Instructions]\n{self.character.persona}\n"
                         
                         # Keep global system prompt as well? Maybe usually redundant if card has one.
                         # But let's append it as "System Rules"
                         if self.character.system_prompt:
                              system_prompt += f"\n[System Rules]\n{self.character.system_prompt}\n"
            except Exception as e:
                print(f"Error loading card: {e}")
        
        if not system_prompt:
            # Fallback or No Card
            system_prompt = (
                f"You are {self.character.name}.\n"
                f"Persona: {self.character.persona}\n"
                f"{self.character.system_prompt}\n"
            )

        system_prompt += f"You are currently talking to a visitor named {visitor_name}.\n"
        
        if relationship_context:
            system_prompt += f"\n[Relationship Context]\n{relationship_context}\n"

        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.extend(context)
        
        # Add the latest message
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response: {e}")
            return "..."

# Global LLM Client instance
llm_client = LLMClient()
