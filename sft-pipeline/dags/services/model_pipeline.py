import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer, models, losses
from sentence_transformers import SentenceTransformerTrainer, SentenceTransformerTrainingArguments
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from datasets import Dataset
from peft import get_peft_model, LoraConfig, TaskType
import optuna

class SFTBiEncoderPipeline:
    def __init__(self, model_name, train_df, val_df, test_df, model_save_path="final-lora-model"):
        self.model_name = model_name
        self.train_df = train_df
        self.val_df = val_df
        self.test_df = test_df
        self.model_save_path = model_save_path
        self.model = None
        self.tokenizer = None
        self.base_model = None
        self.train_examples = []
        self.val_examples = []
        self.evaluator = None
        self.best_params = None

    def prepare_examples(self):
        def convert_df(df):
            return Dataset.from_pandas(df[["query", "doc", "label"]].rename(columns={"query": "text1", "doc": "text2"}))
        self.train_examples = convert_df(self.train_df)
        self.val_examples = convert_df(self.val_df)

    def prepare_model_with_lora(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.base_model = AutoModel.from_pretrained(self.model_name)
        lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=["query", "value"],
                                 lora_dropout=0.1, bias="none", task_type=TaskType.FEATURE_EXTRACTION)
        peft_model = get_peft_model(self.base_model, lora_config)
        peft_model.print_trainable_parameters()
        transformer = models.Transformer(self.model_name)
        transformer.auto_model = peft_model
        transformer.tokenizer = self.tokenizer
        pooling = models.Pooling(word_embedding_dimension=transformer.get_word_embedding_dimension(),
                                 pooling_mode_mean_tokens=True)
        self.model = SentenceTransformer(modules=[transformer, pooling])

    def create_evaluator(self):
        self.evaluator = EmbeddingSimilarityEvaluator(
            list(self.val_examples["text1"]),
            list(self.val_examples["text2"]),
            list(self.val_examples["label"]),
            name="val-set"
        )

    def run_optuna(self, n_trials=20):
        def objective(trial):
            learning_rate = trial.suggest_float("learning_rate", 1e-6, 1e-3, log=True)
            batch_size = trial.suggest_categorical("batch_size", [8, 16, 32])
            num_epochs = trial.suggest_int("num_train_epochs", 2, 8)
            warmup_ratio = trial.suggest_float("warmup_ratio", 0.0, 0.3)
            loss_fn = losses.CosineSimilarityLoss(self.model)
            args = SentenceTransformerTrainingArguments(
                output_dir="optuna-lora",
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                learning_rate=learning_rate,
                warmup_ratio=warmup_ratio,
                logging_steps=100,
                fp16=torch.cuda.is_available(),
                report_to=[]
            )
            trainer = SentenceTransformerTrainer(
                model=self.model,
                args=args,
                train_dataset=self.train_examples,
                eval_dataset=self.val_examples,
                loss=loss_fn,
                evaluator=self.evaluator
            )
            trainer.train()
            result = self.evaluator(self.model, output_path=None)
            return result["val-set_spearman_cosine"]

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)
        self.best_params = study.best_trial.params
        print("Best hyperparameters:", self.best_params)

    def train_final_model(self):
        args = SentenceTransformerTrainingArguments(
            output_dir=self.model_save_path,
            num_train_epochs=self.best_params["num_train_epochs"],
            per_device_train_batch_size=self.best_params["batch_size"],
            per_device_eval_batch_size=self.best_params["batch_size"],
            learning_rate=self.best_params["learning_rate"],
            warmup_ratio=self.best_params["warmup_ratio"],
            fp16=torch.cuda.is_available(),
            logging_steps=50,
            report_to=[]
        )
        trainer = SentenceTransformerTrainer(
            model=self.model,
            args=args,
            train_dataset=self.train_examples,
            eval_dataset=self.val_examples,
            loss=losses.CosineSimilarityLoss(self.model),
            evaluator=self.evaluator
        )
        trainer.train()
        self.model.save(self.model_save_path)
