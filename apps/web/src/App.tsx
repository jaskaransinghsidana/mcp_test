import { FormEvent, useMemo, useState } from 'react';

type Message = { role: 'user' | 'assistant'; content: string };

type AgentTask = {
  id: string;
  title: string;
  description: string;
  status: string;
  tool?: string;
  tool_input?: Record<string, unknown>;
  output?: unknown;
};

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export function App() {
  const [history, setHistory] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<AgentTask[]>([]);

  const canSend = useMemo(() => input.trim().length > 0 && !loading, [input, loading]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!canSend) return;

    const userMessage: Message = { role: 'user', content: input.trim() };
    const nextHistory = [...history, userMessage];
    setHistory(nextHistory);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage.content, history: nextHistory }),
      });

      const payload = await response.json();
      setPlan(payload.plan ?? []);
      setHistory((prev) => [...prev, { role: 'assistant', content: payload.answer ?? 'No response.' }]);
    } catch (error) {
      setHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Unable to reach backend: ${String(error)}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <header className="hero">
        <h1>Agentic MCP Chat</h1>
        <p>LangGraph planning agent + FastMCP tools + modern chat UI</p>
      </header>

      <main className="layout">
        <section className="chat-card">
          <div className="messages">
            {history.length === 0 ? (
              <p className="placeholder">Ask anything to start the agent workflow.</p>
            ) : (
              history.map((msg, idx) => (
                <article key={idx} className={`bubble ${msg.role}`}>
                  <span>{msg.content}</span>
                </article>
              ))
            )}
          </div>

          <form onSubmit={handleSubmit} className="composer">
            <input
              placeholder="Ask the agent a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button disabled={!canSend}>{loading ? 'Thinking...' : 'Send'}</button>
          </form>
        </section>

        <aside className="plan-card">
          <h2>Execution Plan</h2>
          {plan.length === 0 ? (
            <p className="placeholder">The agent plan appears after each response.</p>
          ) : (
            <ul>
              {plan.map((task) => (
                <li key={task.id}>
                  <div className="task-topline">
                    <strong>{task.title}</strong>
                    <span className={`status ${task.status}`}>{task.status}</span>
                  </div>
                  <p>{task.description}</p>
                  <small>
                    Tool: <code>{task.tool ?? 'none'}</code>
                  </small>
                </li>
              ))}
            </ul>
          )}
        </aside>
      </main>
    </div>
  );
}
