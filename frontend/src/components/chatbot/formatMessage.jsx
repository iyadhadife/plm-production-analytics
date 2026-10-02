// Light formatting of bot answers: titles, numbered/bullet lists, **bold**.

const TITLE = /^(🏆|🚨|📊|⚠️|👥|💡|ℹ️|✅|❌)/u;
const NUMBERED = /^\d+\.\s/;
const BULLET = /^[•·→►]\s/;
const SUB_ITEM = /^\s{2,}(•|·|⏱️|📋|⚠️|👉)/u;

const withBold = (text) =>
  text.split(/(\*\*.*?\*\*)/g).map((part, i) =>
    part.startsWith('**') && part.endsWith('**') ? <strong key={i}>{part.slice(2, -2)}</strong> : <span key={i}>{part}</span>,
  );

const lineClass = (line) => {
  if (TITLE.test(line)) return 'message-title';
  if (NUMBERED.test(line)) return 'message-list-item numbered';
  if (BULLET.test(line) || line.trim().startsWith('•')) return 'message-list-item bullet';
  if (SUB_ITEM.test(line)) return 'message-sub-item';
  return 'message-line';
};

export default function formatMessage(text) {
  if (!text) return null;
  return text.split('\n').map((line, i) => {
    if (line.trim() === '') return <br key={i} />;
    const className = lineClass(line);
    const content = className === 'message-sub-item' ? line.trim() : line;
    return (
      <div key={i} className={className}>
        {withBold(content)}
      </div>
    );
  });
}
