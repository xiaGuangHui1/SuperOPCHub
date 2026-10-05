import { useState } from "react";
import { PageMeta } from "@/components/common/PageMeta";
import { Header } from "@/components/generated/Header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { submitRecord } from "@/lib/api";

export default function Record() {
  const [form, setForm] = useState({
    name: "",
    url: "",
    role: "独立开发者",
    description: "",
    skills: "",
    github: "",
  });
  const [status, setStatus] = useState<"idle" | "submitting" | "done" | "error">("idle");
  const [error, setError] = useState("");

  const update = (key: string, value: string) => setForm((p) => ({ ...p, [key]: value }));

  const handleSubmit = async () => {
    if (!form.url.trim()) {
      setError("网站 URL 必填");
      setStatus("error");
      return;
    }
    setStatus("submitting");
    setError("");
    try {
      await submitRecord(form);
      setStatus("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "提交失败");
      setStatus("error");
    }
  };

  return (
    <>
      <PageMeta title="网站备案 - Super OPC Hub" description="提交你的个人网站，进入匹配池" />
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white pb-20">
        <Header />
        <main className="pt-20 px-4 sm:px-6">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-700 mb-2 text-center">网站备案</h2>
            <p className="text-gray-500 text-center mb-8">提交你的网站，让需求方更容易找到你</p>

            {status === "done" ? (
              <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center">
                <p className="text-green-700 font-medium text-lg">备案成功 🎉</p>
                <p className="text-gray-500 mt-2">你的网站已进入匹配池，需求方搜索时优先可见</p>
                <Button
                  className="mt-4"
                  onClick={() => {
                    setStatus("idle");
                    setForm({ name: "", url: "", role: "独立开发者", description: "", skills: "", github: "" });
                  }}
                >
                  再备案一个
                </Button>
              </div>
            ) : (
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 space-y-4">
                <div className="grid gap-2">
                  <Label htmlFor="url">网站 URL *</Label>
                  <Input id="url" value={form.url} onChange={(e) => update("url", e.target.value)} placeholder="https://example.com" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="name">网站名称</Label>
                  <Input id="name" value={form.name} onChange={(e) => update("name", e.target.value)} placeholder="张三的博客" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="role">角色定位</Label>
                  <Input id="role" value={form.role} onChange={(e) => update("role", e.target.value)} placeholder="独立开发者" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="description">一句话介绍</Label>
                  <Textarea id="description" value={form.description} onChange={(e) => update("description", e.target.value)} placeholder="做微信小程序和网站" rows={3} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="skills">技能标签（逗号分隔）</Label>
                  <Input id="skills" value={form.skills} onChange={(e) => update("skills", e.target.value)} placeholder="微信小程序,React,Node.js" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="github">GitHub 链接</Label>
                  <Input id="github" value={form.github} onChange={(e) => update("github", e.target.value)} placeholder="https://github.com/xxx" />
                </div>
                {error && <p className="text-red-500 text-sm">{error}</p>}
                <Button className="w-full" onClick={handleSubmit} disabled={status === "submitting"}>
                  {status === "submitting" ? "提交中..." : "提交备案"}
                </Button>
              </div>
            )}
          </div>
        </main>
      </div>
    </>
  );
}
