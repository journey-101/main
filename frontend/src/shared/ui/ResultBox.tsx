type ResultBoxProps = {
  title: string;
  value: unknown;
};

export function ResultBox({ title, value }: ResultBoxProps) {
  const content = typeof value === "string" ? value : JSON.stringify(value, null, 2);

  return (
    <div className="result-box">
      <h2 className="result-box__title">{title}</h2>
      <pre className="result-box__content">{content}</pre>
    </div>
  );
}
